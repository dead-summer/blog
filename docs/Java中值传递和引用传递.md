---
title: Java中值传递和引用传递
createTime: 2025/07/01 20:17:43
permalink: /article/sjnf7uz2/
---
在 Java 编程中，理解“值传递”（Pass by Value）和“引用传递”（Pass by Reference）的概念对于理解方法参数的传递方式至关重要。这两种传递方式直接影响到方法调用时参数的处理方式以及方法对参数的修改是否会影响到调用者。尽管 Java 中的参数传递方式被称为“值传递”，它在处理对象时表现得类似于“引用传递”。

下面通过一个简单的示例来说明值传递与引用传递的差别：

```java
class Person {  
    String name;  
    Person(String name) { this.name = name; }  
    void setName(String name) { this.name = name; }  
  
    @Override  
    public String toString() { return "Person{name='" + name + "'}"; }  
}  
  
public class TestPass {  
    public static void main(String[] args) {  
        System.out.println("------------------------------------------------------------");  
  
        // 重新赋值无效  
        Person p = new Person("Alice");  
        System.out.println("调用前 p = " + p);  
  
        changeName(p);  
        System.out.println("调用 changeName 后 p = " + p);  
  
        reassign(p);  
        System.out.println("调用 reassign 后 p = " + p);  
  
        System.out.println("------------------------------------------------------------");  
  
        // swap 无效  
        Person Tom = new Person("Tom");  
        Person Jack = new Person("B");  
        System.out.println("交换前 Tom = " + Tom + ", Jack = " + Jack);  
        swap(Tom, Jack);  
        System.out.println("swap 方法返回后 Tom = " + Tom + ", Jack = " + Jack);  
  
        System.out.println("------------------------------------------------------------");  
    }  
    // 修改对象内部状态  
    static void changeName(Person person) {  
        person.setName("Bob");  
    }  
    // 尝试重新赋值引用  
    static void reassign(Person person) {  
        person = new Person("Charlie");  
    }  
    // 试图交换两个引用  
    static void swap(Person x, Person y) {  
        Person tmp = x;  
        x = y;  
        y = tmp;  
    }}
```

运行结果：

```
------------------------------------------------------------
调用前 p = Person{name='Alice'}
调用 changeName 后 p = Person{name='Bob'}
调用 reassign 后 p = Person{name='Bob'}
------------------------------------------------------------
交换前 Tom = Person{name='Tom'}, Jack = Person{name='B'}
swap 方法返回后 Tom = Person{name='Tom'}, Jack = Person{name='B'}
------------------------------------------------------------
```

**分析：**

1. **Java 只有“值传递”（pass-by-value）：**
    
    - 当我们把 `p` 传给 `changeName` 时，传递的是变量 `p` 中存放的 **引用的副本**。
    - 在 `changeName` 内部，通过这个引用副本调用 `setName`，改变了对象的内部状态，因此主调方法看到了名字从 `"Alice"` 变为 `"Bob"`。
        
2. **重新赋值引用不影响外部变量：**
    
    - 在 `reassign` 方法中，我们把局部参数 `person` 指向了一个新的 `Person("Charlie")` 对象。
    - 但这里改变的只是局部参数的“引用副本”，并没有改变外面 `p` 本身所存的引用。因此回到 `main`，`p` 仍然指向原来的对象，名字仍然是 `"Bob"`。
    - 如果 Java 支持真正的引用传递，那么传进去的就不是指针值的副本，而是对外部变量 `p` 本身的一个别名（alias）。这样在方法里重新赋值就会直接修改调用处的变量，使 `p` 指向新的对象。
        
3. **试图交换两个引用也不会生效：**
    
    - `swap(Tom, Jack)` 想把 `Tom` 和 `Jack` 互换，但方法内对 `x`、`y` 的交换只是在它们的局部副本上进行，不会影响外部的 `Jack`、`Tom`。
    - 结果调用后，`Tom`、`Jack` 仍然保持原来的各自指向。

如果 Java 支持真正的“引用传递”（pass-by-reference），则在 `reassign` 或 `swap` 方法中重新赋值、交换引用，都会反映到调用者那里。但 Java 仅仅是把引用的 **值**（即指针）复制一份交给方法，因此无法通过重新赋值来改变调用者的引用。