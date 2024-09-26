```mermaid
graph TD
    subgraph UserInterface
        style UserInterface fill:#F9E79F,stroke:#F39C12,stroke-width:2px;
        A[User] --> B[CRISH]
        A --> C[CloudBeaver]
        A --> D[MinIO S3]
        style B fill:#D4E6F1,stroke:#2980B9,stroke-width:2px;
        style C fill:#D4E6F1,stroke:#2980B9,stroke-width:2px;
        style D fill:#D4E6F1,stroke:#2980B9,stroke-width:2px;
    end

    subgraph Backend
        style Backend fill:#D5F5E3,stroke:#27AE60,stroke-width:2px;
        B --> E[Database Proxy]
        C --> E
        E --> F[PostgreSQL]
        D --> F
        B --> G[MinIO S3]
        style E fill:#A9DFBF,stroke:#1E8449,stroke-width:2px;
        style F fill:#A9DFBF,stroke:#1E8449,stroke-width:2px;
        style G fill:#A9DFBF,stroke:#1E8449,stroke-width:2px;
    end

    subgraph IdentityManagement
        style IdentityManagement fill:#FADBD8,stroke:#E74C3C,stroke-width:2px;
        B --> H[Keycloak]
        C --> H
        D --> H
        H --> G
        style H fill:#F5B7B1,stroke:#C0392B,stroke-width:2px;
    end

    subgraph AuditLogging
        style AuditLogging fill:#F4D03F,stroke:#F1C40F,stroke-width:2px;
        E --> I[Audit Log System]
        style I fill:#F7DC6F,stroke:#F39C12,stroke-width:2px;
    end
```

- **User Interface**: Represents the user's interaction with the system, including accessing the CRISH web app, CloudBeaver for data management, and MinIO S3 for file storage.
- **Backend**: Consists of the PostgreSQL database for storing data and the MinIO S3 storage for managing files. The CRISH communicates with PostgreSQL and MinIO.
- **Identity Management**: Keycloak handles Identity and Access Management (IAM) for the CRISH, CloudBeaver, and MinIO. All these components authenticate with Keycloak.

