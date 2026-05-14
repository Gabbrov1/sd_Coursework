# University Full-Stack Web Project

![Bournemouth University](https://img.shields.io/badge/Bournemouth_University-System_Development-gray?style=flat-square)
![Astro](https://img.shields.io/badge/Astro-React-8a2be2?style=flat-square&logo=astro)
![TypeScript](https://img.shields.io/badge/TypeScript-blue?style=flat-square&logo=typescript&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-REST_API-green?style=flat-square&logo=flask)
![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-4DB33D?style=flat-square&logo=mongodb&logoColor=white)
![MSSQL](https://img.shields.io/badge/MSSQL-SQL-CC2927?style=flat-square&logo=microsoftsqlserver&logoColor=white)
![Cloudflare Pages](https://img.shields.io/badge/Cloudflare_Pages-Deployed-F38020?style=flat-square&logo=cloudflare&logoColor=white)

A full-stack web application built for the **System Development Assignment** at Bournemouth University. The project covers end-to-end design and development of a website with a custom REST API and Google OAuth integration.

---

## Overview

This project fulfils the following assignment requirements:

- Full website designed and developed from scratch
- Custom REST API built with Flask
- At least one Google Services API integrated (Google OAuth)
- Two distinct database types used (SQL and NoSQL)
- Public release of the final project

---

## Tech Stack

### Frontend

| Technology | Purpose |
|---|---|
| Astro + React | Static-first framework with interactive islands |
| TypeScript | Strongly typed development |
| Cloudflare Pages | Free frontend hosting |

### Backend

| Technology | Purpose |
|---|---|
| Flask | REST API server |
| MSSQL | User details and general project data |
| MongoDB | Customisable and dynamic website content |
| Render | Free backend hosting |
| NGrok | Port-forwarding for local database access |

### API Integration

| Integration | Purpose |
|---|---|
| Google OAuth 2.0 | Sign in / sign up with Google account |

---

## Deployment

- **Frontend:** Cloudflare Pages (free static hosting)
- **Backend:** Render (free tier)
- **Databases:** Run locally and exposed via NGrok. This was chosen to avoid the cost of managed MSSQL hosting.

---

## Known Issues

> **Login / CORS bug**
>
> After a successful Google OAuth login, the page resets immediately and logs the user out. The issue is a conflict between the OAuth redirect flow and the CORS configuration. A fix was not implemented within the project timeline.

---

## Assignment Context

This project was submitted as part of the **System Development** module at **Bournemouth University**. Public release was an optional assignment requirement, fulfilled by deploying the frontend and backend to free hosting platforms.

## 📸 Screenshots 

![App screenshot](https://raw.githubusercontent.com/Gabbrov1/sd_Coursework/main/docs/sysDev.JPG)

![App screenshot](https://raw.githubusercontent.com/Gabbrov1/sd_Coursework/main/docs/img1.jpeg)
![App screenshot](https://raw.githubusercontent.com/Gabbrov1/sd_Coursework/main/docs/img2.jpeg)
![App screenshot](https://raw.githubusercontent.com/Gabbrov1/sd_Coursework/main/docs/img3.jpeg)
![App screenshot](https://raw.githubusercontent.com/Gabbrov1/sd_Coursework/main/docs/img4.jpeg)
