# Microservices Architecture Patterns

## Key Principles

1. **Decentralization**
   - Decentralized data management
   - Decentralized governance
   - Independent deployment
   
2. **Organization Around Business Capabilities**
   - Services align with business domains
   - Cross-functional teams own services
   - Few inter-service dependencies

3. **Product Thinking**
   - Teams own their services end-to-end
   - Direct customer interaction
   - Monitor their own services

## Common Patterns

### Decomposition Patterns
- Decompose by business capability
- Decompose by subdomain
- Strangler fig pattern for migration

### Communication Patterns
- Synchronous: REST, gRPC
- Asynchronous: Message queues, event streaming
- API gateway for public interfaces

### Data Management
- Database per service
- Saga pattern for distributed transactions
- Event sourcing for state management

### Deployment Patterns
- Service per container
- Independent scaling
- Orchestration with Kubernetes/similar
