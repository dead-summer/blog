---
title: finally 中的代码一定会被执行吗
createTime: 2025/09/04 18:34:36
permalink: /notes/interview/lj1p8t3g/
---
在 Java 中，`finally` 块中的代码通常被设计为无论 `try` 块中是否发生异常，都会被执行，以确保资源清理等操作的可靠性。然而，在某些极端或异常情况下，`finally` 块中的代码可能不会被执行。

以下是 `finally` 块代码不被执行的几种情况：

1.  **程序在 `try` 块中通过 `System.exit()` 强制退出**
    当程序在 `try` 块中调用 `System.exit(int status)` 方法时，Java 虚拟机（JVM）会立即终止当前正在运行的程序，而不会执行 `finally` 块中的代码。
    ```java
    public class FinallyExample {
        public static void main(String[] args) {
            try {
                System.out.println("执行 try 代码.");
                System.exit(0); // 程序在此处终止
            } finally {
                System.out.println("执行 finally 代码."); // 不会被执行
            }
        }
    }
    ```

2.  **程序在 `try` 块中通过 `Runtime.getRuntime().halt()` 强制终止 JVM**
    `Runtime.getRuntime().halt(int status)` 方法用于强制终止当前正在运行的 Java 虚拟机。与 `System.exit()` 不同，`halt()` 方法不会触发 JVM 的正常关闭序列，这意味着它不会执行关闭钩子（shutdown hooks）或终结器（finalizers），因此 `finally` 块中的代码也不会被执行。
    ```java
    public class FinallyExample {
        public static void main(String[] args) {
            try {
                System.out.println("执行 try 代码.");
                Runtime.getRuntime().halt(0); // 强制终止 JVM
            } finally {
                System.out.println("执行 finally 代码."); // 不会被执行
            }
        }
    }
    ```

3.  **程序在 `try` 块中进入死循环或发生死锁**
    如果 `try` 块中的代码逻辑导致程序进入无限循环（死循环）或者多个线程之间发生死锁，程序可能永远无法正常跳出 `try` 块，从而导致 `finally` 块中的代码无法被执行。

4.  **物理电源故障（掉电）**
    如果程序在执行到 `finally` 块之前，计算机发生突然断电，那么 `finally` 块中的代码自然不会有机会执行。这属于外部环境因素，超出了程序控制范围。

5.  **JVM 异常崩溃**
    当发生严重的 JVM 内部错误（例如，内存溢出 `OutOfMemoryError`、栈溢出 `StackOverflowError` 且无法被捕获处理，或者 JVM 本身崩溃）时，JVM 可能无法继续正常执行，导致 `finally` 块中的代码无法被执行。

