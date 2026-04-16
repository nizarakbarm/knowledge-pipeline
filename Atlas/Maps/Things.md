---
up:
  - "[[Home]]"
created: 2025-04-17
in:
  - "[[Atlas/Maps/Maps]]"
aliases:
  - Things Map
---

This is where I keep tabs on the objective "Things" I have encountered.

What are "Things"? They are the sturdy dots that answer "What is this?" — concepts, frameworks, tools, definitions, places, and known facts. They provide a stable, objective foundation upon which I can hang my subjective "Statement" notes.

> [!Code]- ### Programming Languages
> ```dataview
> TABLE WITHOUT ID
>  file.link as Thing
> FROM "Atlas/Dots/Things/Golang" OR "Atlas/Dots/Things/Python" OR "Atlas/Dots/Things/Rust"
> WHERE !contains(file.name, "Template")
> SORT file.name asc
> ```

> [!Server]- ### Systems & Infrastructure
> ```dataview
> TABLE WITHOUT ID
>  file.link as Thing
> FROM "Atlas/Dots/Things"
> WHERE
> 	!contains(file.path, "Golang") and
> 	!contains(file.path, "Python") and
> 	!contains(file.path, "Rust") and
> 	!contains(file.name, "Template")
> SORT file.name asc
> ```

I am playing around with a property field called `in`. It allows me a nice way to create a few passive maps for different types of things into different collections. Here's what I have so far, feel free to make more:

- [[Golang]] | [[Python]] | [[Rust]] | [[eBPF-Saturday]] | [[BCC eBPF]] | [[Firecracker]] | [[Openlitespeed]] | [[PythonBPF]] | [[Suricata]] | [[Openresty]] | [[Migrating from asdf to mise]] | [[Agenda Python Docs]]

> [!Box]- ## ALL THINGS
> This is a simple dataview pulling anything from the **Things** folder.
> 
> ```dataview
> TABLE WITHOUT ID
>  join(in) as Type,
>  file.link as Thing
> FROM "Atlas/Dots/Things"
> WHERE
> 	contains(in,link("Things")) and
> 	!contains(file.name, "Template")
> SORT file.name asc
> ```

Not included here, but in my personal vault, I enjoy checking out the comprehensive [[Things MOC]] and perusing my [[Toolbox 🧰]]. And to honor the connections, I also keep a [[Concepts Map]] based on tags.

> [!NOTE]+ This is a sanitized version of my actual note. 
> - Content and links have been removed.
