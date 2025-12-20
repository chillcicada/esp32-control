#import "@preview/simple-handout:0.1.0": define-config

#let (
  /// entry options
  twoside,
  use-font,
  /// layouts
  meta,
  doc,
  front-matter,
  main-matter,
  back-matter,
  /// pages
  font-display,
  cover,
  preface,
  outline-wrapper,
  notation,
  figure-list,
  table-list,
  equation-list,
  bilingual-bibliography,
) = define-config(
  info: (
    title: (
      title: "自动连续pH调节与混匀",
      subtitle: "制造工程训练 4-2 组文档",
    ),
    authors: (
      (
        name: "侯仁哲",
        email: "",
      ),
      (
        name: "单明悦",
        email: "",
      ),
      (
        name: "刘宽",
        email: "liukuan22@mails.tsinghua.edu.cn",
      ),
      (
        name: "江宇萱",
        email: "",
      ),
    ),
    version: "0.0.0",
  ),
  font: (
    SongTi: (
      (name: "Times New Roman", covers: "latin-in-cjk"),
      "NSimSun",
    ),
    HeiTi: (
      (name: "Arial", covers: "latin-in-cjk"),
      "SimHei",
    ),
    KaiTi: (
      (name: "Times New Roman", covers: "latin-in-cjk"),
      "KaiTi",
    ),
    FangSong: (
      (name: "Times New Roman", covers: "latin-in-cjk"),
      "FangSong",
    ),
    Mono: (
      (name: "DejaVu Sans Mono", covers: "latin-in-cjk"),
      "SimHei",
    ),
    Math: (
      "New Computer Modern Math",
      "KaiTi",
    ),
  ),
  bibliography: bibliography.with("refs.bib"),
)

/// Document Configuration
#show: meta

/// Cover Page
#cover()

/// After Cover Layout, basical layout for Front Matter, Main Matter and Back Matter
#show: doc

/// ------------ ///
/// Front Matter ///
/// ------------ ///

#show: front-matter

// Preface Page
#preface[]

// Outline Page
#outline-wrapper()

/// ----------- ///
/// Main Matter ///
/// ----------- ///

#show: main-matter

= 项目概述

= 系统架构

= 电路设计

电路设计部分由刘宽同学和单明悦同学共同完成。

= 运动设计

运动设计部分初稿由侯仁哲同学完成，后续在组内讨论的基础上进行了多次迭代和优化。

= 模型设计

侯仁哲同学负责了全项目的模型设计和迭代，

= 程序设计

程序设计部分由刘宽同学，完成的内容如下：

- 完成对嵌入部分代码的重构、拆分和优化；
- 完成 Dobot Magician TCP 外部控制协议的完整实现；
- 实现对整体系统的通信、控制和调试。

以下是各个部分的具体内容：

== 嵌入式代码设计

== Dobot Magician TCP 外部控制协议实现

参考 Dobot 提供的二次开发文档，完成对 Dobot Magician 机械臂的 TCP 外部控制协议的实现。该协议允许通过 TCP/IP 网络对机械臂进行远程控制和操作。

Dobot Magician 机械臂的可以独立的 TCP 客户端模式进行运行，而不依赖预运行的脚本，默认情况下，Dobot Magician 机械臂开放 29999 端口用于 TCP 通信，30001 ～ 30004 端口用于状态数据的实时传输。

==

= 工作日志

/// ----------- ///
/// Back Matter ///
/// ----------- ///

// #show: back-matter

// #notation[]

// #figure-list()

// #table-list()

// #equation-list()

// #bilingual-bibliography()
