---
title: String
createTime: 2025/09/04 16:24:33
permalink: /notes/interview/8sblk5d2/
---
## String 底层数据类型

在不同的 JDK 版本中，`String` 底层数据类型的实现有所不同：

*   **JDK 8 及以前版本**：`String` 底层使用 `char` 类型的数组存储字符序列。
    ```java
    private final char value[];
    ```

    这种实现方式在处理非 ASCII 字符时，每个字符占用两个字节，即使是 ASCII 字符也占用两个字节，可能导致内存空间的浪费。

*   **JDK 9 及以后版本**：`String` 底层改用 `byte` 类型的数组存储字符序列，并增加了一个 `coder` 字段来标识编码格式（`LATIN1` 或 `UTF16`）。
    ```java
    private final byte[] value;
    private final byte coder; // 0 for LATIN1, 1 for UTF16
    ```

    这种优化被称为 Compact Strings。对于只包含 Latin-1 字符（即 ASCII 字符和扩展 ASCII 字符，占用一个字节）的字符串，`String` 会使用 `LATIN1` 编码，每个字符占用一个字节，从而节省内存。对于包含非 Latin-1 字符的字符串，则使用 `UTF16` 编码，每个字符占用两个字节。

## String 的不可变性实现原理

`String` 对象的不可变性（Immutable）是指 `String` 对象一旦创建，其内部的字符序列就不能被改变。其实现原理如下：

1. **底层存储数组被 `final` 和 `private` 修饰**：
    存储字符序列的数组都 `final` 和 `private` 关键字修饰。
    * `private` 确保了 `value` 数组不能被外部直接访问。
    * `final` 确保了 `value` 引用一旦初始化后就不能指向其他数组对象。虽然 `final` 数组本身的内容是可变的，但 `String` 类并没有提供改变 `value` 数组内容的方法。

2. **没有提供修改字符串内容的方法**：
    `String` 类本身没有提供任何公共方法来修改 `value` 数组中的字符或字节。所有看似修改 `String` 对象的操作（如 `concat()`、`substring()`、`replace()` 等）实际上都是创建并返回一个新的 `String` 对象，而原 `String` 对象保持不变。

3. **`String` 类不能被继承**：
    `String` 类被 `final` 修饰，这意味着它不能被继承。这进一步保证了其不可变性，因为如果 `String` 可以被继承，子类可能会重写方法或引入新的行为来修改字符串内容，从而破坏 `String` 的不可变性。

## String 存储的长度限制

`String` 存储的长度存在限制，但这个限制在编译期和运行期有所不同：

1. **编译期限制**：
    在 Java 编译时，字符串常量被存储在字节码文件的常量池中。`CONSTANT_Utf8_info` 结构用于表示字符串常量的值。这个结构使用 `u2 length` 字段来表示字符串的 UTF-8 编码字节长度，其最大值为 65535（即 $2^{16}-1$）。
    因此，在编译期，一个单独的字符串字面量（例如 `String s = "..."`）的长度不能超过 65535 个字节（注意是字节长度，不是字符长度）。

2. **运行期限制**：
    在运行期，`String` 对象的实际长度由其内部 `value` 数组的长度决定。`String` 类的 `length()` 方法返回的是 `value` 数组的长度，而这个长度是用 `int` 类型表示的。
    `int` 类型的最大值为 `Integer.MAX_VALUE`，即 $2^{31}-1$。因此，理论上 `String` 对象在运行期可以存储的最大字符数是 $2^{31}-1$。
    然而，实际能够创建的 `String` 对象长度还会受到 Java 虚拟机（JVM）可用内存的限制。

