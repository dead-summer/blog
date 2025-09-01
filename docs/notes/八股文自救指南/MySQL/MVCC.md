---
title: MVCC
createTime: 2025/07/24 22:24:22
permalink: /notes/interview/rybt9ct0/
---

## 工作原理

**MVCC (Multi-Version Concurrency Control)** 是一种通过维护数据行多版本实现并发控制的技术，核心目标是允许读写操作**无锁并发执行**。

在 MySQL InnoDB 引擎中，它实现了 **READ COMMITTED**（读已提交）和 **REPEATABLE READ**（可重复读）两个隔离级别的并发控制。

MVCC 的实现主要依赖于以下三个核心组件：

1. **隐藏字段 (Hidden Columns)**: InnoDB 会在每行数据后面添加两个隐藏字段：
    - `trx_id`: 记录了最后一个修改该数据行的事务 ID。
    - `roll_pointer`: 指向该数据行的上一个版本，这些历史版本存储在 Undo Log 中，通过 `roll_pointer` 形成一个版本链。
	
2. **Undo Log (回滚日志)**: Undo Log 主要用于存储数据的历史版本。当事务需要修改数据时，会将旧版本的数据快照存入 Undo Log，形成版本链。
    
3. **Read View (读视图)**: 事务在查询时生成的数据可见性快照，包含：
    - `m_ids`: 创建 Read View 时，系统中所有活跃事务的 ID 列表。
    - `min_trx_id`: `m_ids` 列表中的最小事务 ID。
    - `max_trx_id`: 创建 Read View 时，系统下一个将要分配的事务 ID（即当前最大事务 ID + 1）。
    - `creator_trx_id`: 创建该 Read View 的事务自身的 ID。

## 可见性判断逻辑

当一个事务尝试读取某一行数据时，InnoDB 会获取该行数据的最新版本，并将其 `trx_id` 与当前事务的 Read View 进行比较，遵循以下规则来判断数据的可见性：

1. 如果 `trx_id` 与 `creator_trx_id` 相同，意味着是当前事务自己修改了该行数据，因此该版本对当前事务可见。
    
2. 如果 `trx_id` 小于 `min_trx_id`，意味着修改该版本的事务在当前事务创建 Read View 之前就已经提交，因此该版本对当前事务可见。
    
3. 如果 `trx_id` 大于或等于 `max_trx_id`，意味着修改该版本的事务在当前事务创建 Read View 之后才开启，因此该版本对当前事务不可见。此时，需要通过 `roll_pointer` 沿着 Undo Log 版本链查找上一个版本的数据，并重新进行可见性判断。
    
4. 如果 `trx_id` 在 `min_trx_id` 和 `max_trx_id` 之间，则需要进一步判断 `trx_id` 是否存在于 `m_ids` 列表中：
    - **如果存在**: 说明在创建 Read View 时，修改该版本的事务仍然是活跃状态（未提交），因此该版本对当前事务不可见。同样需要沿着 Undo Log 版本链查找上一个版本。
    - **如果不存在**: 说明在创建 Read View 时，修改该版本的事务已经提交，因此该版本对当前事务可见。

## 不同隔离级别下的实现差异

**读已提交 (READ COMMITTED)** 和**可重复读 (REPEATABLE READ)** 两个隔离级别的主要区别在于创建 Read View 的时机不同：

| **隔离级别** | **Read View 创建时机**           | **影响**                               |
| -------- | ---------------------------- | ------------------------------------ |
| **读已提交** | 每次执行 `SELECT` 时创建新 Read View | 可能读到其他事务已提交的数据，导致 **不可重复读**。         |
| **可重复读** | 仅在第一次 `SELECT` 时创建 Read View | 后续所有 `SELECT` 复用同一视图，保证 **可重复读**一致性。 |
