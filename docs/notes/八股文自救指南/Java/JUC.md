---
title: JUC
createTime: 2025/07/24 22:37:54
permalink: /notes/interview/we3gifnt/
---
## CountDownLatch

### CountDownLatch 的底层实现原理是什么？你用它做过什么功能？

`CountDownLatch` 是 Java 并发包 (`java.util.concurrent`) 中的一个同步工具类，它允许一个或多个线程等待其他一组线程完成操作。

#### 底层实现原理

`CountDownLatch` 的底层实现依赖于 `AbstractQueuedSynchronizer` (AQS)，这是一个用于构建锁和同步器的框架。`CountDownLatch` 内部有一个继承了 AQS 的同步器 `Sync`。

其核心原理如下：

1. **初始化状态**：在创建 `CountDownLatch` 对象时，会传入一个整型参数 `count`，这个值会被设置为 AQS 内部的 `state` 变量。这个 `state` 代表了需要等待完成的操作数量。
    
2. **`await()` 方法**：
    
    - 当一个线程调用 `await()` 方法时，它会检查当前的 `state` 值。
        
    - 如果 `state` 的值为 `0`，表示所有需要等待的操作已经完成，`await()` 方法会立即返回。
        
    - 如果 `state` 的值不为 `0`，该线程会被封装成一个 `Node` 节点，并加入到 AQS 的同步等待队列中，然后线程被挂起 (park)，进入休眠状态，等待被唤醒。
        
3. **`countDown()` 方法**：
    
    - 当一个任务完成时，它会调用 `countDown()` 方法。
        
    - 此方法会以线程安全的方式（通过 CAS 操作）将 `state` 的值减 `1`。
        
    - 当 `state` 的值被减到 `0` 时，意味着所有等待的事件都已发生。此时，`countDown()` 方法会唤醒 (unpark) 所有在同步队列中等待的线程。

总结来说，`CountDownLatch` 通过 AQS 的 `state` 变量来作为计数器。`await()` 操作依赖于 `state` 是否为 `0` 来决定是否阻塞线程，而 `countDown()` 操作则递减 `state`，并在 `state` 归零时唤醒所有等待的线程。

#### 应用场景

我曾在一个数据初始化场景中使用过 `CountDownLatch`。系统启动时，需要并行地从多个不同的数据源（如数据库、缓存、第三方 API）加载初始化数据。主线程必须等待所有数据都加载完毕后，才能继续执行后续的业务逻辑（例如，对外提供服务）。

具体实现如下：

1. 创建一个 `CountDownLatch`，其计数器的初始值设置为数据源的数量，例如 `new CountDownLatch(3)`。
    
2. 为每个数据加载任务创建一个独立的线程，并在任务的 `run()` 方法中执行数据加载逻辑。
    
3. 在每个数据加载线程的 `finally` 块中，调用 `latch.countDown()` 方法，确保无论加载成功与否，计数器都会减一。
    
4. 主线程在启动所有数据加载线程后，立即调用 `latch.await()` 方法。此时，主线程会阻塞，直到计数器变为 `0`。
    
5. 当所有数据加载任务都执行完毕并调用了 `countDown()` 后，计数器归零，主线程从 `await()` 方法中被唤醒，继续执行后续的启动流程。

通过这种方式，`CountDownLatch` 优雅地实现了主线程对多个并行任务完成状态的等待，提升了系统的启动效率。
