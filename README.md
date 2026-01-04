# Conceptual-Exploration-with-LLM

This project is currently under active development and is being supervised by [Dr. Sergei Obiedkov](https://iccl.inf.tu-dresden.de/web/Sergei_Obiedkov/en), this repository contains part one of the project which is attribute and object exploration, the part containing semantic maps will be shared soon

## 1. Project Overview

### 1.1. Objective 

The primary goal is to analyze linguistic data (e.g., cross-linguistic meanings and lexical groupings) using FCA and then **verify the resulting implications** through LLMs. These implications capture logical patterns such as:

- **Attribute implications**:  
  > If a verb expresses meanings A and B, then it also expresses C.

- **Object implications**:  
  > If meanings A and B co-occur in certain lexical items, they also appear in others.

The system supports exploration and verification of **both types**, giving users full control over how they interrogate the conceptual structure of the data.

The second goal is to utilize the generated data to create various semantic maps using different algorithms, such as randomized algorithms, and conduct a comparative study. This part of the project is being handled by my colleague, [Prathamesh Rane](https://github.com/prathameshrane08) [Repo will be shared soon]

### 1.2. Methodology

The project follows a two-step process:

1. **Formal Concept Analysis** is applied to lexical typology data to generate a set of implications (attribute-based and object-based).
2. These implications are then validated by a **Large Language Model**, with support for various user interaction modes.

### 1.3. Validation Modes

Three verification modes have been developed, each suited to different levels of automation:

#### 1.3.1. Manual Mode
- The user manually validates each implication using their own linguistic knowledge.
- Ideal for experts seeking precise control.

#### 1.3.2. Assisted Mode
- The LLM provides proposed answers and justifications.
- Users can **interactively chat** with the system:
  - Ask follow-up questions
  - Challenge the model
  - Refine or explore counterexamples
- Useful for guided, collaborative research.

#### 1.3.3. Automated Mode
- Operates with minimal user input.
- Automatically validates implications until:
  - All implications are resolved, or
  - A user-defined limit (e.g., *X* implications) is reached.
- Suitable for large-scale or batch validation tasks.


By combining **formal logic from FCA** with the **reasoning abilities of LLMs**, this system offers a powerful toolkit for scalable, explainable, and interactive analysis of semantic structure in language data—supporting both **attribute** and **object exploration** modes.

## 2. Background: Formal Concept Analysis (FCA)

**Formal Concept Analysis (FCA)** is a mathematical framework for data analysis that focuses on identifying and visualizing relationships between a set of **objects** and a set of **attributes**. Developed by Rudolf Wille in the early 1980s, FCA is grounded in **lattice theory** and is widely used in knowledge representation, data mining, and ontology engineering.

### 2.1. Formal Context

Think of this as a simple table showing "what has what" - like a spreadsheet where rows are objects, columns are attributes, and checkmarks shows that this specific attribute is present in that object.

formally, A **formal context** in FCA is a triple: 

K = (G, M, I)

Where:
- **G** is a set of **objects**
- **M** is a set of **attributes**
- **I** is a binary relation (subset of G × M) indicating which object has which attribute  
  (i.e., (g, m) ∈ I means object *g* has attribute *m*)

For example concider the below formal concept which represents a small set of **person categories** based on their **gender** and **age group**.:


|        Object        | Female | Male | Juvenile | Adult |
|:--------------------:|:------:|:----:|:--------:|:-----:|
| **girl**             |   ✔️   |      |    ✔️    |       |
| **woman**            |   ✔️   |      |          |  ✔️   |
| **boy**              |        |  ✔️  |    ✔️    |       |
| **man**              |        |  ✔️  |          |  ✔️   |

^Taken from [upriss.github.io](https://upriss.github.io/fca/fcaintro.html)


In this context the **Objects** are `girl`, `woman`, `boy`, `man` and the **Attributes** are `female`, `male`, `juvenile`, `adult`. Each object is described by the attributes that apply to it, like A **girl** is **female** and **juvenile**

This setup defines a simple logical structure where each object can be classified by its gender and age. It allows us to explore patterns and relationships—like grouping all **juveniles**, all **females**, or all **adults**—based on shared attributes.


### 2.2. Formal Concepts

A **formal concept** is a pair:

(A, B)

Where:
- **A** ⊆ G is the **extent** (the set of objects sharing the attributes in B)
- **B** ⊆ M is the **intent** (the set of attributes common to all objects in A)

These satisfy the following conditions:

A = { g ∈ G | ∀ m ∈ B: (g, m) ∈ I }

B = { m ∈ M | ∀ g ∈ A: (g, m) ∈ I }

From our context, below are some formal concepts can be derived:

1. **({girl}, {female, juvenile})**  
2. **({woman}, {female, adult})**  
3. **({boy}, {male, juvenile})**  
4. **({man}, {male, adult})**  

These concepts form the building blocks of the **concept lattice**, which organizes them hierarchically based on shared attributes and object groupings.

These formal concepts form a **concept lattice**, which reveals hierarchical relationships among concepts.

For our example we get the below lattice daigram

<img width="296" height="246" alt="Screenshot 2025-07-14 at 11 14 11 PM" src="https://github.com/user-attachments/assets/275c7df2-b9b0-4909-87fa-ac709e3ca703" />

### 2.3. Attribute Implications and Attribute exploration 

An **attribute implication** is a rule of the form:

X → Y

Where X, Y ⊆ M. This means:

> If an object has all the attributes in set X, then it also has all the attributes in set Y.

These implications capture dependencies between attributes and can be used for reasoning and data compression. FCA provides tools to compute a minimal (canonical) set of such implications, known as the **Duquenne–Guigues basis**.

> **Attribute Exploration** is a procedure in which we ask a expert is this implication 𝑋 → 𝑌 valid? The expert then has two options. Either, the expert accepts 𝑋 → 𝑌 as a valid implication in the domain, or, he refutes the implication. In the latter case the expert is obliged to present a counter example in the “language” of the domain, i.e., an object described by the attributes from 𝑀 (initial context).

### 2.4. Object Implications

**Object implications** are less commonly used and arise in the **dual** setting of FCA:

A → B

Where A, B ⊆ G. This means:

> If all objects in A share certain attributes, then the same holds for objects in B.

While analogous to attribute implications, object implications are mainly explored in theoretical extensions of FCA.

> **Object Exploration** is also done in a similar manner as the attribute exploration .

## 3. Data Description: Lexical Typology

The targeted datasets that can be used by our system comes from the field of **Lexical Typology**, a branch of linguistic typology that studies how different languages categorize and lexicalize concepts across the **semantic space**.

### 3.1. Context

While:
- **Phonological typology** focuses on the sound systems (phonemes) of languages
- **Grammatical typology** deals with morphological patterns and word forms

**Lexical typology** explores **how languages structure word meanings**, especially how they split or merge conceptual domains.

### 3.2. Example: The Word *Thick*

In English, the adjective *thick* can describe:
- Dimensional size (e.g., *thick wall*, *thick stick*)
- Substance consistency (e.g., *thick porridge*)

However, in Russian, these meanings are split between two distinct words:
- **толстый (*tolstyj*)**: for dimensional size (*толстая стена* – thick wall)
- **густой (*gustoj*)**: for consistency (*густая каша* – thick porridge)

This demonstrates how **semantic domains** are divided differently across languages.

### 3.3. Example of actual dataset

A sample of the actual data used in our analysis is shown below.

<img width="785" height="436" alt="Screenshot 2025-07-14 at 11 42 28 PM" src="https://github.com/user-attachments/assets/916fa77d-5c49-4d80-b599-103bb7ff520b" />

## 4. Tools and framewords used:
- **[Shiny for Python](https://shiny.posit.co/py/)**  
  Shiny is a framework for building interactive web applications in Python. It allows you to create rich, reactive user interfaces entirely in Python, without needing to write JavaScript. In this project, Shiny powers the frontend UI and handles user interactions, data uploads, and real-time updates.

- **[OpenAI API](https://platform.openai.com/)**  
  The OpenAI API is used to integrate AI-driven functionality, such as natural language processing or decision support. In this application, we use the API to send our formatted prompts and receive answers, helping enhance the analysis process.

- **[FCATNG Library](https://github.com/tomhanika/fcatng)**  
  FCATNG (Formal Concept Analysis Tools – Next Generation) is a Python library for performing **Formal Concept Analysis (FCA)**. It supports working with contexts, implications, concept lattices, and attribute exploration. This library forms the core of the application's logical engine, enabling implication generation, validation, and management of formal contexts.

## 4. System Overview

### 4.0. System Architecture 

<img width="1379" height="722" alt="Screenshot 2025-07-24 at 11 20 56 AM" src="https://github.com/user-attachments/assets/8828198e-6404-4f8e-801b-9eabf9efe473" />

### 4.1. File Upload Page

The initial screen allows users to upload their context files to the system. Supported formats include Excel (.xlsx), CSV (.csv), and CXT (.cxt). Users can select a file from their device, which the system then processes for further analysis. 

<img width="1582" height="961" alt="Screenshot 2025-07-14 at 11 49 56 PM" src="https://github.com/user-attachments/assets/8d3fb5a3-2751-4a77-8bb7-f6d3babefb33" />

The user can also select using the slider which rows and columns to use for analysis.

<img width="1582" height="961" alt="Screenshot 2025-07-14 at 11 57 09 PM" src="https://github.com/user-attachments/assets/c3cdd222-f9fd-4ed2-9ad6-ece33075eda7" />

### After the initial file upload, user can then select among attribute exploration or object exploration.

### 4.2. Attribute Exploration

#### 4.2.1 Manual Mode

When the system first loads, it automatically displays the first available implication by default. Users can browse and select other implications from a list on the right-hand side of the screen. Selecting a different implication updates the view dynamically to reflect the chosen data.

<img width="1582" height="961" alt="Screenshot 2025-07-14 at 11 57 48 PM" src="https://github.com/user-attachments/assets/5962575e-1c57-41b1-aa91-f92e974c0db8" />

When a user confirms an implication, it is added to the Confirmed Implications section located on the right-hand side of the screen. This section provides a running list of all implications the user has reviewed and approved, helping track progress and decisions during the analysis.

<img width="1582" height="961" alt="Screenshot 2025-07-14 at 11 59 23 PM" src="https://github.com/user-attachments/assets/4526c904-eeb1-44ac-ba1c-923650a23632" />

if a user rejects an implication, the system prompts them to provide a counterexample. This counterexample is then validated by the system:
- If the counterexample is valid, it is added as a new object to the formal context.
- If the counterexample is invalid, the system displays a relevant error message indicating why it was not accepted.

<img width="1582" height="961" alt="Screenshot 2025-07-14 at 11 58 02 PM" src="https://github.com/user-attachments/assets/677fa2df-d254-4077-9316-ed2de6328b94" />
<img width="1582" height="961" alt="Screenshot 2025-07-15 at 12 07 09 AM" src="https://github.com/user-attachments/assets/dd606df2-f521-4d7f-975b-38f8a5f0e080" />

#### 4.2.2 Assisted Mode

When the system first loads in assisted mode, it displays an “Ask the Model” button. When the user clicks this button, the system sends a prompt containing all relevant information about the context, the current implication, and other constraints to the LLM model. The model’s response is then displayed to the user.

<img width="1582" height="961" alt="Screenshot 2025-07-15 at 12 16 08 AM" src="https://github.com/user-attachments/assets/c1d0ce88-3200-4cad-9129-824639eb4218" />

The system then gives the user several options:

1. Confirm the response from the model
   - If the model's response was that the implication is valid, then the implication will be added to confirmed implication section.
   - If the model’s response includes a valid counterexample, it will be added to the context.
   - If the counterexample is invalid, the system will notify the user.
2. Provide manual input, which functions the same as in manual mode.
3. Chat with the model for further interaction.
4. View the prompt that was sent to the model.

<img width="1470" height="919" alt="Screenshot 2025-07-15 at 12 19 13 AM" src="https://github.com/user-attachments/assets/44a0ce92-5f23-4ead-ac8c-52e48fb952c1" />

If the user selects the **Chat** option, they can engage with the model by asking questions like why a particular counterexample was chosen or requesting alternative counterexamples in different languages.  

> **Important:** In chat mode, the system generates free-flowing, conversational responses by default, without attempting to automatically parse them as input for system integration. This approach supports flexible, natural interaction without incurring the overhead or risk of misinterpreting loosely structured output.
> However, when the user identifies a counterexample during the conversation that they deem valid and worth incorporating, they must explicitly instruct the system to parse it by issuing a command such as:
“Please parse the previous result to the system.”

>This design ensures that only intentional, user-validated data is processed, maintaining system integrity and reducing parsing errors. It strikes a deliberate balance between conversational freedom and controlled data input, making the system both robust and user-directed.

<img width="1470" height="919" alt="Screenshot 2025-07-15 at 12 34 02 AM" src="https://github.com/user-attachments/assets/a5c63e09-d698-46d3-910f-86e648d0378a" />

#### 4.2.3 Auto Mode

In this mode, the system prompts the user to input a **system prompt**, which can include instructions such as specifying which languages the counterexamples should include or exclude. It also asks for the number of implications to be validated before the system terminates.

The process terminates when either there are no more implications to process or the number of implications specified by the user is reached. Once complete, the system displays logs detailing all actions taken for each implication during the validation process.

<img width="1470" height="919" alt="Screenshot 2025-07-15 at 12 37 40 AM" src="https://github.com/user-attachments/assets/7362c04f-19ef-49b7-9bbc-9b9a04c51fc1" />

### 4.3 Object Exploratoin

Object exploration shares the same UI features as attribute exploration. The key difference is that the implications involved are object implications instead of attribute implications.

<img width="1582" height="961" alt="Screenshot 2025-07-15 at 1 00 20 AM" src="https://github.com/user-attachments/assets/4e481f77-feff-4ee1-96bb-6b0d3c93015f" />

### 4.4 Exports

The context can be exported by the user at any time, either in **CXT format** or as a **CSV dataframe**, using the two button at the buttom right corner of the page.

<img width="1582" height="961" alt="Screenshot 2025-07-15 at 12 54 56 AM" src="https://github.com/user-attachments/assets/1d0d5502-9fb9-48a5-9952-32f46c318ae1" />





