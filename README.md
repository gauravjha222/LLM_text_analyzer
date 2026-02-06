# LLM Response Analysis

This project analyzes responses from multiple Large Language Models (LLMs) for the same user query and extracts common meaningful patterns such as property types (BHK) and price ranges.
The goal is to keep the logic simple, transparent, and easy to explain, while avoiding unnecessary complexity or paid API overuse.

## Problem Statement

Different LLMs often give long and descriptive answers for the same question.
Manually comparing them is time-consuming and messy.
This project solves that by:

* Collecting responses from multiple LLMs

* Extracting useful structured information

* Identifying common patterns across models

* Keeping the original model responses for transparency


# Approach (High-Level)

## 1. Input Query
A single natural language query (example: “rent in koramangala”)

## 2. Multiple LLM Responses
The same query is sent to:

ChatGPT

Gemini

Llama

## 3. Information Extraction
From each response, we extract:

BHK types (1BHK, 2BHK, etc.)

Price values (₹ amounts above ₹10,000)

## 4. Common Pattern Analysis
Find overlapping BHK types and price points across all models.

## 5. Final Structured Output
Output includes:

Model name

Raw response text

Extracted analysis

Common patterns across models
