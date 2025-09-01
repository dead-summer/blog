---
title: Unsafe类
createTime: 2025/08/27 15:59:11
permalink: /notes/interview/3r4exvjh/
---
## 概述

`Unsafe` 类是 Java 中一个底层工具类，位于 `sun.misc` 包下，用于提供绕过 JVM 限制的硬件级别操作。由于 Java 无法直接访问底层操作系统，它通过本地 (native) 方法实现这些功能，本质上作为 JVM 的一个“后门”。该类广泛应用于并发编程中（如 CAS 操作），但需谨慎使用，因其操作可能破坏 Java 的内存安全和类型安全机制。

## 核心作用

`Unsafe` 是 CAS (Compare-And-Swap) 操作的核心实现基础。它通过硬件级别的原子指令，支持高效的并发控制。在 JUC (Java Util Concurrent) 包和三方框架（如 Netty、Disruptor）中，`Unsafe` 被用于保证并发安全性和性能优化。

## 主要功能

`Unsafe` 提供以下关键功能：

- **内存管理**：分配堆外内存（例如 `allocateMemory` 方法）和释放内存（例如 `freeMemory` 方法）。分配的内存不受 JVM GC 管理，需手动释放以避免内存泄漏。
- **对象操作**：定位对象字段的内存偏移量（例如 `objectFieldOffset` 方法），并直接修改字段值（包括私有字段），例如通过 `putXXX` 系列方法。
- **线程控制**：挂起线程（例如 `park` 方法）和恢复线程（例如 `unpark` 方法），支持线程调度优化。
- **CAS 操作**：提供原子性的比较并交换（例如 `compareAndSwapXXX` 方法），用于实现无锁并发数据结构。
- **其他基础操作**：包括数组操作（例如 `arrayBaseOffset`）、内存屏障（例如 `loadFence/storeFence`）和栅栏 (Fence) 操作，确保指令顺序性和可见性。

## 使用场景

在 JDK 源码（如 `AtomicXXX` 类、`LockSupport`、`ConcurrentHashMap`）中，`Unsafe` 用于优化性能。它通过直接操作内存和硬件指令，减少 JVM 开销，适用于高并发系统、低延迟框架和底层库开发。

## 风险与注意事项

`Unsafe` 是一把“双刃剑”：

- **优点**：提供高性能底层访问，提升效率。
- **风险**：
	- 手动内存管理易导致内存泄漏或溢出。
	- 绕过访问控制（例如修改私有字段）可能破坏封装性和稳定性。
	- 非标准 API，不同 JDK 版本实现可能变动，影响兼容性。

