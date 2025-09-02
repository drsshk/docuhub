# Project Document Flow

This document outlines the step-by-step lifecycle of a `Project` within the DocuHub application, from its creation to final approval and versioning.

### 1. Creation (Draft Stage)

*   **Who:** A user with a "Submitter" role.
*   **What:** The Submitter creates a new `Project`. This project is assigned a unique name and is automatically set to `Version 1`.
*   **System State:** The project's status is `Draft`.
*   **Actions:** While in the `Draft` state, the Submitter can edit the project details and, most importantly, add, edit, or delete `Drawings` associated with it.

### 2. Submission for Approval

*   **Who:** The Submitter.
*   **What:** Once all drawings are added and the project is ready, the Submitter clicks a "Submit" button.
*   **System State:** The project's status changes to `Pending_Approval`.
*   **System Actions:**
    *   An entry is created in the `ApprovalHistory` to log the submission event.
    *   The notification service sends two emails:
        *   A confirmation email to the Submitter.
        *   A notification email to all users with "Admin" or "Approver" roles, alerting them of the new submission.

### 3. Review

*   **Who:** A user with an "Admin" or "Approver" role.
*   **What:** The Approver accesses a dedicated review dashboard where they see all projects currently in the `Pending_Approval` status. They review the project details and its associated drawings.
*   **System State:** The project remains `Pending_Approval`.

### 4. The Decision

The Approver makes a decision, which triggers one of the following outcomes:

*   **a. Approval**
    *   **Action:** The Approver clicks "Approve".
    *   **System State:** The project's status changes to `Approved_Endorsed`.
    *   **System Actions:** The decision is logged in `ApprovalHistory`, and an approval notification email is sent to the original Submitter.

*   **b. Rejection**
    *   **Action:** The Approver clicks "Reject" and must provide comments explaining the reason.
    *   **System State:** The project's status changes to `Rejected`.
    *   **System Actions:** The rejection and comments are logged in `ApprovalHistory`, and a rejection email (including the comments) is sent to the Submitter.

*   **c. Request for Revision**
    *   **Action:** The Approver clicks "Request Revision" and provides comments on what needs to be changed.
    *   **System State:** The project's status changes to `Request_for_Revision`.
    *   **System Actions:** The request is logged in `ApprovalHistory`, and an email with the required revisions is sent to the Submitter.

### 5. Versioning (Creating a New Version)

This is how the project evolves after feedback or for a new iteration.

*   **Who:** The Submitter.
*   **What:** The Submitter initiates a "Create New Version" action on an existing project (this is typically done on a project that is `Approved_Endorsed`, `Rejected`, or requires revision).
*   **System Actions:**
    *   The system creates a **new** `Project` record with the same name but an incremented version number (e.g., Version 2).
    *   It automatically copies all the drawings from the previous version into this new version.
    *   The **old** project's status is automatically set to `Obsolete`.
    *   The new project starts fresh in the `Draft` status, and the entire lifecycle (from step 1) begins again.

This flow ensures a complete audit trail, clear separation of roles, and a structured process for document submission, review, and version management.
