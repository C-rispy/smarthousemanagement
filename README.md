# Smart House — Dictionary-Based Object System in Python

A simplified smart home management system implemented *without* Python's built-in `class` system.  
All devices and inheritance behavior are modeled using plain dictionaries — a constraint from the course that helped reinforce how object systems work under the hood.

> Built as part of the Software Construction course at UZH.  
> Original project completed in collaboration with my colleagues **Bleron Neziri** and **Cynthia Ka Ong**.

---

## 🚀 Project Summary

This project simulates multiple smart home devices (Lights, Thermostats, Cameras) and manages them through a central controller. It features:

- An object-oriented design using dictionary templates
- Custom dynamic dispatch with a `call()` method and recursive `find()` lookup
- Multiple inheritance support
- Connection-capable devices with tracking of IP and connection status
- Computation of energy use for:
  - all devices
  - devices by type (e.g., only Lights)
  - devices by room (e.g., only Bedroom)
  - devices connected to a specific IP
- Descriptive string output for all devices

Because we weren’t allowed to use Python classes, this project demonstrates a deep understanding of **abstraction**, **encapsulation**, and **method resolution** independent of Python’s OOP sugar.

---

## 🧩 System Overview

Device types supported:

| Device       | Inherits From            | Unique Attributes                      | Power Formula Example                                                      |
|--------------|-------------------------|----------------------------------------|---------------------------------------------------------------------------|
| Light        | `Device`                 | `brightness` (%)                       | `round(base_power * brightness / 100)`                                   |
| Thermostat   | `Device`, `Connectable` | `room_temperature`, `target_temperature` | `base_power * abs(target_temperature - room_temperature)`                 |
| Camera       | `Device`, `Connectable` | `resolution_factor`                    | `base_power * resolution_factor`                                         |

The SmartHouseManagement system aggregates all devices created using a custom `make()` constructor function.

Behind the scenes, a custom dispatch system ensures polymorphic behavior:

`call(obj, "method_name")` → resolve method via `find()` → invoke with obj as argument


---

## 🧪 Custom Testing Framework

Instead of Python’s built-in testing libraries, tests are executed via:

- Introspection-based test discovery  
- Custom reporting: **pass / fail / error**
- Per-test execution timing
- Command-line filtering

**Run tests:**

```bash
python test_smart_house.py
python test_smart_house.py --select thermostat
python test_smart_house.py --verbose
```
---

## 🧠 Key Learnings

Working under these constraints helped develop:

- Understanding of polymorphism without classes
- Designing reusable components using delegation
- Automated validation through internal testing tools
- Git collaboration and clean software engineering processes
- Building OO semantics out of dictionaries feels like constructing a machine out of LEGO pieces — no hidden magic, every mechanism visible and intentional.

---

## 📂 Repository Structure

smart_house.py        # Core implementation (dictionary-based OOP)
test_smart_house.py   # Custom dynamic test suite
README.md             # This document

---

## 📌 Attribution

This repository represents my personal portfolio version of the project.
Course collaboration credits:

- Thierry Mathys
- Bleron Neziri
- Cynthia Ka Ong
