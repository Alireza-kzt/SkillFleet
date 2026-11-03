---
name: fleet-flutter
description: Build and review Flutter/Dart features, especially GetX applications, with focused widgets, explicit controller lifecycles, testable domain behavior and consistent navigation, error and loading states.
---

# Flutter and GetX

1. Read pubspec.yaml, analysis_options.yaml, the relevant feature, routing, bindings and state conventions. Keep the current architecture unless migration is requested.
2. Let widgets describe layout and interaction. Keep request parsing, persistence and nontrivial business rules outside build methods. Extract widgets around reusable behavior or a meaningful boundary.
3. Use the project's GetX bindings for ownership. Initialize work in the appropriate lifecycle method; dispose streams, workers, subscriptions and text/animation controllers in onClose or dispose.
4. Use the smallest reactive scope. Keep network calls out of build. Choose Obx/GetBuilder according to existing patterns rather than wrapping a whole screen.
5. Make loading, empty, success, error and retry states explicit. Prevent duplicate submissions and updates after disposal. Preserve server error meaning while presenting readable UI text.
6. Use typed models and clear nullability. Keep JSON conversion at the data boundary. Do not create an interface, use case and repository for a trivial local calculation.
7. Check small screens, keyboard insets, large text, accessibility labels and RTL. Reuse the project's theme and design tokens.
8. Run dart format, flutter analyze and relevant tests when the SDK is available. Exercise the changed flow on an available device; state if device verification was unavailable.
