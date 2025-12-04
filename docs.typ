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

= 运动设计

= 模型设计

= 程序设计

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
