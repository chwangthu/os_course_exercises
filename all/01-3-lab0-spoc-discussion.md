# lec2：lab0 SPOC思考题

## **提前准备**
（请在上课前完成，option）

- 完成lec2的视频学习
- git pull ucore_os_lab, os_tutorial_lab, os_course_exercises  in github repos。这样可以在本机上完成课堂练习。
- 了解代码段，数据段，执行文件，执行文件格式，堆，栈，控制流，函数调用,函数参数传递，用户态（用户模式），内核态（内核模式）等基本概念。思考一下这些基本概念在不同操作系统（如linux, ucore,etc.)与不同硬件（如 x86, riscv, v9-cpu,etc.)中是如何相互配合来体现的。
- 安装好ucore实验环境，能够编译运行ucore labs中的源码。
- 会使用linux中的shell命令:objdump，nm，file, strace，gdb等，了解这些命令的用途。
- 会编译，运行，使用v9-cpu的dis,xc, xem命令（包括启动参数），阅读v9-cpu中的v9\-computer.md文档，了解汇编指令的类型和含义等，了解v9-cpu的细节。
- 了解基于v9-cpu的执行文件的格式和内容，以及它是如何加载到v9-cpu的内存中的。
- 在piazza上就学习中不理解问题进行提问。

---

## 思考题

- 你理解的对于类似ucore这样需要进程/虚存/文件系统的操作系统，在硬件设计上至少需要有哪些直接的支持？至少应该提供哪些功能的特权指令？

  需要硬件支持时钟中断，虚存需要通过MMU转换，文件系统需要可靠存储介质的支持。特权指令应该有允许和禁止中断，控制中断禁止屏蔽位，进程切换，存储保护，执行I/O等。

- 你理解的x86的实模式和保护模式有什么区别？你理解的x86的实模式和保护模式有什么区别？你认为从实模式切换到保护模式需要注意那些方面？

  实模式只有16位寻址空间，对应内存；而保护模式有32位寻址空间，进程收到保护。切换时应该注意寻址空间变化，进程保护，寄存器的更改等。

- 物理地址、线性地址、逻辑地址的含义分别是什么？它们之间有什么联系？

  物理地址就是对应到内存最终的地址，逻辑地址是访问指令中给出的地址，通过段页转换可得到物理地址；线性地址是逻辑地址到物理地址中间的转换阶段。

- 你理解的risc-v的特权模式有什么区别？不同模式在地址访问方面有何特征？

  机器模式是可以执行的最高的权限模式，最重要的特性是拦截和处理异常的能力，地址空间是物理内存空间。

  用户模式不可以执行特权指令，例如eret，并且只能访问自己的那部分内存。

  监督者模式位于机器模式和用户模式之间，使用基于页面的虚拟内存。

  一旦发生异常都会转移到M模式。

- 理解ucore中list_entry双向链表数据结构及其4个基本操作函数和ucore中一些基于它的代码实现（此题不用填写内容）

- 对于如下的代码段，请说明":"后面的数字是什么含义
```
 /* Gate descriptors for interrupts and traps */
 struct gatedesc {
    unsigned gd_off_15_0 : 16;        // low 16 bits of offset in segment
    unsigned gd_ss : 16;            // segment selector
    unsigned gd_args : 5;            // # args, 0 for interrupt/trap gates
    unsigned gd_rsv1 : 3;            // reserved(should be zero I guess)
    unsigned gd_type : 4;            // type(STS_{TG,IG32,TG32})
    unsigned gd_s : 1;                // must be 0 (system)
    unsigned gd_dpl : 2;            // descriptor(meaning new) privilege level
    unsigned gd_p : 1;                // Present
    unsigned gd_off_31_16 : 16;        // high bits of offset in segment
 };
```

unsigned表示unsigned int，(unsigned variable: 数字)的形式表示variable这个变量占所		填充数字那么多的比特位，能够更有效利用空间。

- 对于如下的代码段，

```
#define SETGATE(gate, istrap, sel, off, dpl) {            \
    (gate).gd_off_15_0 = (uint32_t)(off) & 0xffff;        \
    (gate).gd_ss = (sel);                                \
    (gate).gd_args = 0;                                    \
    (gate).gd_rsv1 = 0;                                    \
    (gate).gd_type = (istrap) ? STS_TG32 : STS_IG32;    \
    (gate).gd_s = 0;                                    \
    (gate).gd_dpl = (dpl);                                \
    (gate).gd_p = 1;                                    \
    (gate).gd_off_31_16 = (uint32_t)(off) >> 16;        \
}
```
如果在其他代码段中有如下语句，
```
unsigned intr;
intr=8;
SETGATE(intr, 1,2,3,0);
```
请问执行上述指令后， intr的值是多少？

Intr = 0x20003

### 课堂实践练习

#### 练习一

1. 请在ucore中找一段你认为难度适当的AT&T格式X86汇编代码，尝试解释其含义。

   选取`entry.S`：

   ```assembly
   .text
   .globl kernel_thread_entry
   kernel_thread_entry:        # void kernel_thread(void)
   
       pushl %edx              # push arg
       call *%ebx              # call fn
   
       pushl %eax              # save the return value of fn(arg)
       call do_exit            # call do_exit to terminate current thread
   ```

   这段汇编代码的意思是：首先将参数压栈，调用函数，之后保存函数的返回值，杀死这个线程。

2. (option)请在rcore中找一段你认为难度适当的RV汇编代码，尝试解释其含义。

   `entry.S`:

   ```assembly
       .section .text.entry
       .globl _start
   _start:
       add t0, a0, 1
       slli t0, t0, 16
       
       lui sp, %hi(bootstack)
       addi sp, sp, %lo(bootstack)
       add sp, sp, t0
   
       call rust_main
   
       .section .bss.stack
       .align 12  #PGSHIFT
       .global bootstack
   bootstack:
       .space 4096 * 16 * 8
       .global bootstacktop
   bootstacktop:
   ```

   开始执行

#### 练习二

宏定义和引用在内核代码中很常用。请枚举ucore或rcore中宏定义的用途，并举例描述其含义。

答：宏能够有效减少函数调用，提升程序的运行时间。

```c
#define static_assert(x)                                \
    switch (x) { case 0: case (x): ; }
```

使用该宏，当x为0时会出现编译错误。


## 问答题

#### 在配置实验环境时，你遇到了哪些问题，是如何解决的。

我采用从ubuntu镜像创建虚拟机，通过指导书，没什么问题，但是调试有点小bug还没解决。

## 参考资料
 - [Intel格式和AT&T格式汇编区别](http://www.cnblogs.com/hdk1993/p/4820353.html)
 - [x86汇编指令集  ](http://hiyyp1234.blog.163.com/blog/static/67786373200981811422948/)
 - [PC Assembly Language, Paul A. Carter, November 2003.](https://pdos.csail.mit.edu/6.828/2016/readings/pcasm-book.pdf)
 - [*Intel 80386 Programmer's Reference Manual*, 1987](https://pdos.csail.mit.edu/6.828/2016/readings/i386/toc.htm)
 - [IA-32 Intel Architecture Software Developer's Manuals](http://www.intel.com/content/www/us/en/processors/architectures-software-developer-manuals.html)
 - [v9 cpu architecture](https://github.com/chyyuu/os_tutorial_lab/blob/master/v9_computer/docs/v9_computer.md)
 - [RISC-V cpu architecture](http://www.riscvbook.com/chinese/)
 - [OS相关经典论文](https://github.com/chyyuu/aos_course_info/blob/master/readinglist.md)
