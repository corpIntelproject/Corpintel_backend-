# AI Document Assistant: Database Schema (Optimized Final Version)

## 1. Overview
This is the **Industry Standard Multi-Tenant Architecture**. It uses a single `User` model to handle authentication for everyone, with the `tenant_id` and `role` stored directly on the user. This makes Django authentication seamless while maintaining strict data isolation.

## 2. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    CorpTenant ||--o{ CorpUser : "employs"
    CorpTenant ||--o{ DOCUMENT : "owns files"
    CorpTenant ||--o{ CONVERSATION : "owns chats"
    CorpUser ||--o{ CONVERSATION : "starts & chats in"
    CONVERSATION ||--o{ MESSAGE : "contains"
    DOCUMENT ||--o{ DOCUMENT_ACCESS : "has access rules"
    CorpUser ||--o{ DOCUMENT_ACCESS : "is granted access via"
    CorpTenant {
        uuid tenant_id PK
        string organization_name
        string registration_number
        string company_website
        string headquarters_location
        string industry_type
    }

    CorpUser {
        uuid user_uuid PK
        uuid tenant_profile_id FK "Which company they belong to"
        string username
        string email
        string password
        string first_name
        string system_role "CORP_ADMIN / CORP_EMPLOYEE"
        boolean is_email_verified
        string email_otp
    }
    DOCUMENT {
        uuid id PK
        uuid tenant_id FK "Which company owns this"
        uuid uploaded_by_user_id FK
        string file_name
        string file_url
        string status "Queued, Processing, Indexed"
    }
    
    DOCUMENT_ACCESS {
        uuid id PK
        uuid document_id FK
        uuid user_id FK "Specific user who can read this"
    }

    CONVERSATION {
        uuid id PK
        uuid tenant_id FK "Data boundary"
        uuid user_id FK "Who started the chat"
        string title
    }

    MESSAGE {
        uuid id PK
        uuid conversation_id FK
        string sender "User / AI"
        text content
        json citations
    }
```

## 3. Core Tables Breakdown

### 3.1. CorpTenant Table (The Company)
When a user clicks "Register your Company", a new row is created here.
- **`tenant_id` (PK):** Unique UUID identifier.
- **`organization_name`:** Name of the organization (Unique).
- **`registration_number`:** Corporate ID (CIN/GSTIN).
- **`headquarters_location` / `industry_type`:** Company metadata.

### 3.2. CorpUser Table (All Humans)
Handles ALL logins. Django uses this single table for authentication.
- **`user_uuid` (PK):** Unique UUID identifier.
- **`tenant_profile_id` (FK):** Links the user to their Company. This is critical for data isolation.
- **`email` / `password`:** Standard login credentials.
- **`system_role`:** Defines their permissions. Can be `"CORP_ADMIN"` or `"CORP_EMPLOYEE"`.
- **`is_email_verified` / `email_otp`:** Used for the OTP verification flow.

### 3.3. Document Table
Files uploaded by the Admins.
- **`tenant_id` (FK):** Ties the document to the company, ensuring employees from Company B can never see Company A's files.
- **`uploaded_by_user_id` (FK):** Tracks which Admin uploaded it.

### 3.4. Document_Access Table
Controls granular access to specific documents (Role-Based Access Control).
- **`document_id` (FK):** The document being protected.
- **`user_id` (FK):** Allows a specific User (Employee) to access the document.

### 3.5. Conversation Table
The chat history sessions.
- **`tenant_id` (FK):** Ties the chat to the company's data boundary.
- **`user_id` (FK):** Tracks the specific User (Admin or Employee) who started this chat.

### 3.6. Message Table
The individual chat bubbles inside a Conversation.
- **`conversation_id` (FK):** Links the message to its parent thread.
- **`sender`:** Identifies if the sender is `User` or `AI`.
- **`content`:** The text question or the AI's generated answer.
