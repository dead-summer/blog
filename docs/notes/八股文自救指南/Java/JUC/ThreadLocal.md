---
title: ThreadLocal
createTime: 2025/08/25 20:51:43
permalink: /notes/interview/8s6pd4xf/
---
`ThreadLocal` 提供线程级别的数据存储机制。每个线程拥有独立的 `ThreadLocal` 变量副本，可安全操作数据而无需同步，避免线程间干扰。

## 使用场景

### 典型应用场景

1. **用户身份信息存储**
   在拦截器/过滤器中完成用户鉴权后，将用户 ID、权限等信息存入 `ThreadLocal`，后续请求链路直接从中获取，避免参数透传。
 
2. **线程安全工具类封装**
   为线程不安全类（如 `SimpleDateFormat`）创建独立实例。示例：
	```java
	private static final ThreadLocal<SimpleDateFormat> dateFormat = 
		ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd"));
	```

3. **日志上下文存储**
   日志框架（如 `Logback`）使用 `ThreadLocal` 存储 `traceID`、用户 ID 等上下文信息，实现日志链路追踪。

4. **分布式链路追踪**
   在分布式系统中存储全局唯一的 `traceID`，确保全链路调用可追踪。

5. **数据库会话管理**
   ORM 框架（如 MyBatis）通过 `ThreadLocal` 管理数据库会话（Session），保证线程独享连接，避免并发冲突。

### 核心作用

1. **线程内数据透传**
   在同一线程执行过程中，存储跨方法层级的共享数据，消除参数透传冗余。
 
2. **解决并发安全问题**
   通过线程隔离机制，避免共享资源竞争，实现无锁并发。

## 实现原理

### 数据结构

1. 每个 `Thread` 对象内部维护一个 `ThreadLocalMap` 成员变量。
2. `ThreadLocalMap` 内部维护一个 `Entry` 数组作为哈希表存储结构。
3. 每个 `Entry` 对象包含：
    - Key：`ThreadLocal` 对象（使用弱引用）。
    - Value：存储的实际数据（强引用）。
4. `Entry` 在数组中的位置通过 `ThreadLocal` 的 `threadLocalHashCode` 计算得出。
5. 单个线程可关联多个 `ThreadLocal` 实例。
```java
// Thread 类内部维护
ThreadLocal.ThreadLocalMap threadLocals;

// ThreadLocalMap 结构
static class ThreadLocalMap {
    static class Entry extends WeakReference<ThreadLocal<?>> {
        Object value;  // 存储的实际数据（强引用）
        Entry(ThreadLocal<?> k, Object v) {
            super(k);  // Key（ThreadLocal 对象）为弱引用
            value = v;
        }
    }
    private Entry[] table;  // 哈希表数组
}
```

### 操作机制

- **`set(T value)`**
	1. 获取当前线程的 `ThreadLocalMap`。
	2. 以当前 `ThreadLocal` 实例为 Key，存储 Value。
	3. 通过 `threadLocalHashCode & (len-1)` 计算数组下标。
	4. 若 `ThreadLocalMap` 不存在则创建新实例。
	```java
	public void set(T value) {
	    Thread t = Thread.currentThread();
	    ThreadLocalMap map = getMap(t);
	    if (map != null) {
	        map.set(this, value);  // 哈希表插入
	    } else {
	        createMap(t, value);   // 创建新哈希表
	    }
	}
	```
- **`get()`**
	1. 获取当前线程的 `ThreadLocalMap`
	2. 以当前 `ThreadLocal` 实例为 Key 查找 `Entry`
	3. 命中则返回 `Entry.value`
	4. 未命中则初始化并返回默认值
	```java
	public T get() {  
	    Thread t = Thread.currentThread();  
	    ThreadLocalMap map = getMap(t);  
	    if (map != null) {  
	        ThreadLocalMap.Entry e = map.getEntry(this);  
	        if (e != null) {  
	            @SuppressWarnings("unchecked")  
	            T result = (T)e.value;  
	            return result;  
	        }
	    }
	    return setInitialValue();  // 初始化并返回默认值
	}
	```

## 内存泄漏问题

### 泄漏场景分析

| 场景        | 内存泄漏风险 | 原因说明                                    |
| --------- | ------ | --------------------------------------- |
| 普通线程      | 无      | 线程结束时，`ThreadLocalMap` 随线程销毁被回收         |
| 线程池（核心线程） | 有      | 线程长期存活，`ThreadLocalMap` 持续持有 Value 的强引用 |

### 泄漏根本原因

1. **强引用链维持**：
	```mermaid
	graph LR
	A[线程Thread] --强引用--> B[ThreadLocalMap]
	B --强引用--> C[Entry数组]
	C --强引用--> D[Entry.value]
	```
    - `Entry` 的 Key（`ThreadLocal` 对象）为**弱引用**，GC 时可回收。
    - `Entry` 的 Value 为**强引用**，在线程存活期间无法回收。

2. **线程复用机制**：
    - 线程池中的核心线程长期存活。
    - 未清理的 `Entry` 导致 Value 持续占用内存。
    - 即使 `ThreadLocal` 实例被回收，Key 变为 `null` 的 `Entry`（僵尸 `Entry`）仍保留 Value 引用。

### 引用类型对比

| 引用类型 | GC 回收条件          | 应用场景                         |
| ---- | ---------------- | ---------------------------- |
| 强引用  | 超出作用域或显式置 `null` | 默认对象引用                       |
| 软引用  | JVM 内存不足时        | 缓存实现                         |
| 弱引用  | 下次 GC 必然回收       | `ThreadLocalMap.Entry` 的 Key |
| 虚引用  | 对象回收时收到系统通知      | 资源清理跟踪                       |

### 避免内存泄漏的解决方案

1. **主动清理**：在任务结束时调用 `remove()` 方法释放资源
2. **防御式编程**：使用 `try-finally` 确保清理执行

```java
try {
    threadLocal.set(data);     // 设置线程局部变量
    // 执行业务逻辑...
} finally {
    threadLocal.remove();      // 强制移除当前线程的 Entry
}
```

::: note 关键点

`remove()` 方法会显式清除当前线程的 `Entry`，断开 Value 的强引用链，确保 GC 可回收内存资源。

:::
