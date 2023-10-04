import unittest
from run import generate_embedding

class TestGenerateEmbedding(unittest.TestCase):
    def test_generate_embedding(self):
        # TODO: Replace with your actual endpoint, API key, and deployment name
        endpoint = ''
        api_key = ''
        deployment_name = ''
        text = 'This is a test text to generate embed.'
        embedding = generate_embedding(text, endpoint, api_key, deployment_name)
        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 512)  # Assuming the embedding size is 512

if __name__ == '__main__':
    unittest.main()
