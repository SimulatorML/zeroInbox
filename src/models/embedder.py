from sentence_transformers import SentenceTransformer
import torch


class TextEmbedder:
    """
    A class for loading and managing SentenceTransformer models.

    Attributes:
        model_name (str): The name of the model to be loaded.
        use_gpu (bool): Flag indicating whether to use GPU if available.
        model (SentenceTransformer): The loaded SentenceTransformer model instance.
    """

    def __init__(self, model_name: str = 'cointegrated/rubert-tiny2', use_gpu: bool = False):
        """
        Initializes a SentenceTransformer model.

        Parameters:
            model_name (str): The name of the model to be loaded. Defaults to 'cointegrated/rubert-tiny2'.
            use_gpu (bool): Flag indicating whether to use GPU if available. Defaults to False.

        Raises:
            ValueError: If the provided model name is empty.
            RuntimeError: If there is an error loading the model on the specified device.
        """
        self.model_name = model_name
        self.use_gpu = use_gpu
        self.model = self.init_model()

    def init_model(self):
        """
        Loads the SentenceTransformer model and assigns it to a device based on the availability of CUDA and the user's preference for using GPU.

        Returns:
            SentenceTransformer: The loaded SentenceTransformer model.
        """
        if self.model_name.strip() == '':
            raise ValueError('Model name cannot be empty.')

        try:
            device = "cuda" if torch.cuda.is_available() and self.use_gpu else "cpu"
            model = SentenceTransformer(self.model_name, device=device)
        except Exception as e:
            raise RuntimeError(f"Failed to load the model '{self.model_name}' on the specified device '{device}'. Error: {e}")

        return model
