---
name: fleet-python
description: Implement or review Python, FastAPI and OpenCV services with clear I/O boundaries, typed contracts, explicit resource lifecycles and meaningful tests. Preserve the project's established Python architecture.
---

# Python services

1. Inspect pyproject.toml or requirements, the app entry point, existing settings, routers and test fixtures. Use the supported Python version and dependency manager.
2. Keep route handlers focused on transport, authentication and validation. Put domain decisions in a cohesive module; keep database, filesystem, GPU and HTTP calls behind a boundary that the task actually needs.
3. Use plain functions and dataclasses or existing validation models before introducing a new service/repository hierarchy. Type public contracts; validate untrusted values at entry.
4. In async endpoints, avoid blocking CPU, OpenCV and filesystem work on the event loop. Use the existing worker/executor strategy. Distinguish cancellation, timeout and validation failures.
5. Use lifespan/context managers for clients, models, temporary files and device resources. Avoid loading a model per request or initializing expensive mutable state during import.
6. Keep configuration in the established settings layer. Never log tokens, raw sensitive requests or complete environment variables.
7. Handle image orientation, color spaces, shape/dtype and empty/corrupt inputs explicitly. State units for geometry and transformations.
8. Test a representative request, an important failure and any modified domain behavior. Verify imports and the project's actual lint/type checks. Avoid a separate mock-heavy test architecture for a small change.
