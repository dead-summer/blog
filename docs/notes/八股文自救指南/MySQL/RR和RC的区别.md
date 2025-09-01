在 MySQL 中，RR (REPEATABLE READ) 和 RC (READ COMMITTED) 是两种不同的事务隔离级别，主要区别体现在快照读行为、锁机制和主从同步要求上。以下是详细对比：

## 快照读 (Snapshot Read)

快照读是一种基于多版本并发控制 (MVCC) 的读取机制，它通过数据的历史版本快照来显示查询结果，而不受其他并发事务的未提交更改影响。

- **适用隔离级别**：仅在 READ COMMITTED 和 REPEATABLE READ 级别下生效。
- **行为差异**：
	- **READ COMMITTED (RC)**：事务中的每次查询前都会创建一个新的 ReadView（快照视图）。新建的 ReadView 会更新除 `creator_trx_id` 外的所有字段，因此可能导致不可重复读现象。
	- **REPEATABLE READ (RR)**：事务仅在第一次查询时创建 ReadView，后续所有查询共享同一个 ReadView，从而解决不可重复读问题。
- **核心原理**：ReadView 的生成时机不同（RC 每次查询新建，RR 首次查询新建），这是 MVCC 实现的关键。

## 锁机制 (Locking Mechanism)

MySQL 使用锁来保证事务的隔离性，RR 和 RC 在锁类型和范围上存在显著差异：

- **锁类型**：
	- **Record Lock**：记录锁，锁定索引记录本身。
	- **Gap Lock**：间隙锁，锁定索引记录之间的间隙（防止新记录插入）。
	- **Next-Key Lock**：Record Lock 和 Gap Lock 的组合，锁定索引记录及其左开右闭的间隙范围（例如 `(a, b]`）。
- **行为差异**：
	- **READ COMMITTED (RC)**：仅使用 Record Lock（针对索引记录加锁），不支持 Gap Lock 或 Next-Key Lock。因此，无法完全防止幻读（Phantom Read）。
	- **REPEATABLE READ (RR)**：支持 Record Lock、Gap Lock 和 Next-Key Lock。通过 Gap Lock 和 Next-Key Lock 锁定索引间隙，有效解决幻读问题。

## 主从同步 (Master-Slave Replication)

在数据主从同步中，BinLog 格式对事务隔离级别有严格要求：

- **BinLog 格式**：MySQL 支持三种格式：
	- **STATEMENT**：基于 SQL 语句的复制。
	- **ROW**：基于行变化的复制。
	- **MIXED**：混合模式，自动选择 STATEMENT 或 ROW。
- **行为差异**：
	- **READ COMMITTED (RC)**：仅支持 ROW 格式的 BinLog。因为 RC 允许不可重复读，基于 STATEMENT 的复制可能导致从库数据不一致。
	- **REPEATABLE READ (RR)**：支持所有格式（STATEMENT、ROW 和 MIXED）。RR 的一致性保证使其兼容基于语句的复制。

## 总结

::: question 为什么互联网公司选择使用 **Read Committed** 隔离级别？

1. 互联网业务的特点：高并发
	- 互联网公司和传统企业最大的差异之一，就是 **并发量**。例如：2020 年双十一当天，订单创建峰值达到 **58.3 万笔/秒**。
	- 要扛得住这种并发量，系统需要在数据库层面尽量减少锁冲突，提高吞吐量。

2. RC 相比 RR 的优势
	- **提升并发度**
		- **RC 隔离级别**：只对被修改的记录加行级锁，不会额外加 Gap Lock 和 Next-Key Lock。
		- **RR 隔离级别**：除了行级锁，还会加 Gap Lock 和 Next-Key Lock，锁范围更大，导致并发度下降。
	
	- **降低死锁概率**
		- RR 因为锁范围更大，多个事务更容易发生 **相互等待**，从而导致死锁。
		- RC 避免了 Gap Lock 和 Next-Key Lock，锁冲突和死锁概率大幅降低。
:::