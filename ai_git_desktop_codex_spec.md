# AI Git Desktop --- Codex Development Specification

## Overview

AI Git Desktop is a **desktop application that allows users to manage
Git and GitHub using natural language instead of command-line
commands**.

The application translates user prompts into Git commands or GitHub API
actions.

Example user input:

    create a repository called weather-app and upload this project

The application should automatically:

1.  Initialize a Git repository
2.  Create a GitHub repository
3.  Commit project files
4.  Push them to GitHub

The user does not need to know Git commands.

------------------------------------------------------------------------

# Objective

Build a desktop tool that removes the complexity of Git for beginners.

Users should be able to:

-   manage repositories
-   commit code
-   push changes
-   create branches
-   open pull requests

All using **natural language**.

------------------------------------------------------------------------

# Target Users

This tool is designed for:

-   beginners learning Git
-   students
-   indie hackers
-   non-technical founders
-   developers who dislike Git CLI

------------------------------------------------------------------------

# High Level Architecture

    User Input
       ↓
    Chat Interface
       ↓
    LLM Command Interpreter
       ↓
    Structured Action
       ↓
    Action Router
       ↓
    Git Engine / GitHub API

------------------------------------------------------------------------

# Technology Stack

## Desktop Application

Preferred stack:

    Tauri
    React
    TypeScript
    TailwindCSS

Alternative stack:

    Electron
    React

------------------------------------------------------------------------

## Backend Logic

    Node.js
    TypeScript

------------------------------------------------------------------------

## Git Integration

Library:

    simple-git

Responsibilities:

-   initialize repository
-   add files
-   commit changes
-   push to remote
-   create branches

------------------------------------------------------------------------

## GitHub Integration

Library:

    Octokit

Responsibilities:

-   create repositories
-   create pull requests
-   list commits
-   list branches

------------------------------------------------------------------------

## AI Command Interpreter

The AI layer converts natural language into structured actions.

Example:

User prompt:

    create a branch called login-feature

AI output:

``` json
{
  "action": "create_branch",
  "branch_name": "login-feature"
}
```

------------------------------------------------------------------------

# Core Modules

## Chat Interface

Location:

    app/frontend/chat

Responsibilities:

-   receive user prompts
-   display assistant responses
-   ask for confirmation when necessary

------------------------------------------------------------------------

## Command Parser

Location:

    core/command-parser

Responsibilities:

-   interpret user prompts
-   generate structured action objects

Example output:

``` json
{
  "action": "push_changes"
}
```

------------------------------------------------------------------------

## Action Router

Location:

    core/action-router

Responsibilities:

-   receive structured actions
-   route them to appropriate modules

Example:

    create_branch → Git Engine
    create_repo → GitHub Service

------------------------------------------------------------------------

## Git Engine

Location:

    core/git-engine

Handles all local Git operations.

Example functions:

    initRepo()
    commitChanges()
    pushChanges()
    createBranch()
    checkoutBranch()

------------------------------------------------------------------------

## GitHub Service

Location:

    core/github-service

Handles all GitHub API operations.

Example functions:

    createRepo()
    createPullRequest()
    listBranches()
    listCommits()

------------------------------------------------------------------------

# Project Folder Structure

    ai-git-desktop
    │
    ├── app
    │   ├── frontend
    │   │   ├── components
    │   │   ├── chat
    │   │   └── pages
    │   │
    │   └── backend
    │       ├── git
    │       ├── github
    │       └── ai
    │
    ├── core
    │   ├── command-parser
    │   ├── action-router
    │   ├── git-engine
    │   └── github-service
    │
    ├── assets
    │
    └── README.md

------------------------------------------------------------------------

# MVP Features

The following features must be implemented first.

## 1 --- Create Repository

User prompt:

    create a repository called my-project

Expected behavior:

-   Create GitHub repository
-   Initialize local Git repo
-   Commit files
-   Push to GitHub

------------------------------------------------------------------------

## 2 --- Commit Changes

User prompt:

    commit my changes

Actions executed:

    git add .
    git commit

------------------------------------------------------------------------

## 3 --- Push Changes

User prompt:

    push my project

Actions executed:

    git push

------------------------------------------------------------------------

## 4 --- Branch Management

User prompt:

    create a branch called feature-login

Actions executed:

    git checkout -b feature-login

------------------------------------------------------------------------

## 5 --- Pull Request

User prompt:

    open a pull request from dev to main

Expected behavior:

-   Use GitHub API
-   Create pull request

------------------------------------------------------------------------

# Command Flow Example

User input:

    create a branch called test-feature

AI interpreter returns:

``` json
{
  "action": "create_branch",
  "branch_name": "test-feature"
}
```

Action router executes:

    git checkout -b test-feature

------------------------------------------------------------------------

# Safety Rules

The application must confirm dangerous actions.

Examples requiring confirmation:

-   delete branch
-   reset repository
-   force push

Example confirmation:

    This action will delete the branch "main".
    Are you sure? (yes/no)

------------------------------------------------------------------------

# Development Plan

AI coding agents should follow this order:

1.  Create project folder structure
2.  Implement Git Engine
3.  Implement GitHub Service
4.  Implement Action Router
5.  Implement Command Parser
6.  Build Chat UI
7.  Connect modules together

------------------------------------------------------------------------

# Coding Guidelines

-   Use TypeScript for backend logic
-   Keep modules small and focused
-   Avoid monolithic files
-   Write clear function names
-   Keep dependencies minimal

------------------------------------------------------------------------

# Future Features

Possible future improvements:

-   AI explanation of Git errors
-   automated commit message generation
-   merge conflict resolution assistant
-   deployment automation
-   visual Git history graph

------------------------------------------------------------------------

# Contribution Rules

AI agents modifying this repository must:

1.  Follow the architecture defined in this document
2.  Avoid restructuring modules unnecessarily
3.  Document new components
4.  Maintain modular design

------------------------------------------------------------------------

# Project Status

Prototype stage.

Current goal:

**Build a working MVP for natural language Git operations.**
