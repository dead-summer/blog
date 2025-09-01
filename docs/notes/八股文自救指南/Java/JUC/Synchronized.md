每个 Java 对象在内存中都有一个对象头（Object Header），其中包含 Mark Word 区域。Mark Word 存储对象的运行时数据，包括哈希码（Hash Code）、锁状态标志位（Lock Flag）、GC 分代年龄（GC Age）等。锁状态标志位标识了 `Synchronized` 的当前状态，为锁升级提供基础支持。

## 实现原理

`Synchronized` 的实现是分层的，涉及 Java 语言、字节码、JVM 逻辑和操作系统等多个层面：

- **语言层面**：
	`synchronized` 是一个关键字，用于修饰代码块或方法。它定义了临界区（Critical Section），确保同一时间只有一个线程能访问共享资源。
	
- **字节码层面**：
	`synchronized` 对应两条 JVM 字节码指令：
	- `monitorenter`：进入临界区，表示需要加锁。
	- `monitorexit`：退出临界区，表示需要解锁。
	这些指令在编译时生成，指导 JVM 在运行时执行锁操作。
	
- **JVM 逻辑层面**：
	JVM 通过 Monitor（监视器）来管理线程竞争。每个锁对象关联一个 Monitor，其内部由三个逻辑区域组成：
	- **Owner**：当前持有锁的线程。
	- **EntryList**：等待锁的阻塞线程队列。当锁被占用时，竞争失败的线程进入此队列阻塞。
	- **WaitSet**：通过 `obj.wait()` 进入等待状态的线程队列。当线程调用 `obj.wait()` 时，会释放锁并加入 WaitSet；等待 `obj.notify()` 唤醒后，重新竞争锁。
	具体流程：
	1. 线程执行 `monitorenter` 时，JVM 检查锁对象的 Monitor。
	2. 若 Owner 为空，线程成为 Owner。
	3. 若 Owner 被占用，线程进入 EntryList 阻塞。
	4. 线程执行 `monitorexit` 时，JVM 释放锁，并唤醒 EntryList 中的线程进行锁竞争。
	
- **操作系统层面**：
	重量级锁（Heavyweight Lock）涉及用户态到内核态的切换，JVM 需向操作系统申请互斥量（Mutex）。这会导致性能开销较大，尤其在频繁加锁的场景中。

### 锁升级过程

`Synchronized` 在 JDK 1.6 后引入了锁升级机制，针对不同线程竞争强度进行优化，过程分为四个阶段：

```mermaid
graph LR
    A[无锁] -->|线程首次访问| B[偏向锁]
    B -->|多个线程竞争| C[轻量级锁]
    C -->|竞争加剧| D[重量级锁]
```

- **无锁到偏向锁**：
	初始状态下，锁为无锁（Lock-Free）。当线程首次进入 `Synchronized` 代码块时，JVM 将锁标记为偏向锁（Biased Lock），并在锁对象的 Mark Word 中记录线程 ID。此后，该线程重入锁时，通过比较线程 ID 直接获取锁，避免了加锁开销。此机制优化了无竞争或低竞争的重入场景。
	
- **偏向锁到轻量级锁**：
	当其他线程尝试获取锁时（竞争出现），JVM 撤销偏向锁。多个线程通过 CAS（Compare-And-Swap）自旋竞争锁：
	1. 将锁对象头的 Mark Word 复制到线程栈的锁记录（Lock Record）中。
	2. 线程尝试 CAS 操作，将 Mark Word 更新为指向锁记录的指针。
	3. 若 CAS 成功，线程获得轻量级锁（Lightweight Lock）。此阶段通过自旋减少阻塞，适用于低至中等竞争场景。
	
- **轻量级锁到重量级锁**：
	当竞争加剧（多个线程短时间高并发请求），轻量级锁的自旋会占用 CPU 资源。JVM 触发锁膨胀（Lock Inflation），将锁升级为重量级锁。重量级锁基于 Monitor 机制，竞争失败的线程直接阻塞（不占用 CPU），由操作系统调度。此机制适配高竞争场景。

Synchronized 的锁升级设计旨在适配不同竞争强度的场景：

- 偏向锁优化单线程重入。
- 轻量级锁通过自旋减少阻塞开销。
- 重量级锁在激烈竞争中避免 CPU 浪费。

该机制平衡了性能与资源利用率，是 Java 并发编程的核心优化之一。
