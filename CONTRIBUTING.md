# Contribution Instruction & Guidelines

Hello there! Any kind of contribution to **BondAI** is most welcome!

- If you have a question, please use GitHub
  [discussions](https://github.com/krohling/bondai/discussions).
- If you found a bug or have a feature request, please use GitHub
  [issues](https://github.com/krohling/bondai/issues).
- If you fixed a bug or implemented a new feature, please do a pull request. If it
  is a larger change or addition, it would be great to first discuss it through an
  [issue](https://github.com/krohling/bondai/issues).

## Development Setup

Warning: If you run **BondAI** on your own system, tools that interact with the file system will have full access to your local disk! I highly recommend running and testing inside of a Docker container.

Always be careful when approving any code!

## Tools

When you contribute code, please use **black** for code formatting. 

## Branching & Release Strategy

The default branch is called master.
It contains the latest features, which would be ready for deployment.
It is not possible to push to it directly.
Instead, for every feature, a branch should be created, which will then be merged back into main with a pull request.

At some point, a new version can be released.
To do so, the version number should be entered in the *VERSION* file.
A release with corresponding release notes can then be generated on GitHub.
This also automatically triggers a deployment to docker hub.

Semantic versioning is used for releases.
If the version number contains a `b` (e.g. `1.0.0b1`), a `nightly` image will be released, otherwise the image will be tagged as `latest`. 