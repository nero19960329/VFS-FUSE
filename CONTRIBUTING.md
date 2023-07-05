Thank you for your interest in contributing to this repository! Before you proceed, please take a moment to review the guidelines below.

## Code Formatting
To maintain a consistent code style, we require that all pull requests (PRs) adhere to the following guidelines:

- Please format your code using `black` before submitting your PR. You can install `black` by running `pip install black`. To format your code, run `black <filename>` or `black .` to format all files in the repository.

## Integration Testing
We have integration tests in place to ensure the reliability and functionality of our codebase. To contribute effectively, please ensure that your changes pass the integration tests located at `./tests/integration/test_file_operations.sh`. Your PR will need to pass these tests to be considered for merging.

## Versioning
We follow semantic versioning for our release process. The version number is determined based on the commits in the repository. Each commit contributes to the versioning process, and the next version is determined automatically.

## Commit Message Guidelines
We kindly request that all commit messages adhere to the conventional commit message format. Conventional commit messages help in maintaining a standardized and informative commit history.

To follow the conventional commit message format, please refer to the guidelines provided in the [Conventional Commits specification](https://www.conventionalcommits.org/en/v1.0.0/). By following this format, you can provide clear and meaningful commit messages that facilitate better understanding and tracking of changes.

## Building Python Package
To build the Python package locally, please follow the steps below:

1. Install or upgrade `setuptools` and `build` by running `pip install --upgrade setuptools build`.
1. Run the command `python -m build --sdist --wheel --outdir dist` in the root directory of the repository.
1. After executing the command, the built package files will be located in the `dist` directory.

Please ensure that the package builds successfully before submitting your PR.

Thank you for your contributions, and we look forward to reviewing your pull request!
