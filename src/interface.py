from abc import ABC, abstractmethod


# NOTE Every API or Model should Implement the following method

class ConfigurableModel(ABC):
    """Abstract base class for models that can be configured."""
    @abstractmethod
    def _initialize(self):
        """Initialize the model based on the configuration."""
        pass


class GenerativeModel(ABC):
    """Abstract base class for generative models."""

    @abstractmethod
    def synthesize(self, input_data):
        """synthesize output based on the input data."""
        pass
