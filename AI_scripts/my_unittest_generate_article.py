import os
import unittest
import logging
from unittest.mock import patch, mock_open, MagicMock

# Import the module containing the functions I want to test.
from generate_article import (
    check_env_variable_error,
    check_env_variable_warning,
    initialize_csv,
    send_telegram_message,
    get_topics_create_csv_and_notify,
    fetch_topic_and_description,
    get_image_create_file_and_notify,
    get_article_content,
    check_and_load_env_variables,
    ensure_directories_exist,
    initialize_files,
    create_article_with_image,
)

class TestMyScript(unittest.TestCase):

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'dummy', 'TELEGRAM_BOT_TOKEN': '', 'TELEGRAM_CHAT_ID': ''})
    def test_check_env_variable_error(self):
        self.assertEqual(check_env_variable_error('OPENAI_API_KEY'), 'dummy')
        with self.assertRaises(ValueError):
            check_env_variable_error('MISSING_ENV_VAR')

    @patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'dummy_token'})
    def test_check_env_variable_warning(self):
        self.assertIsNone(check_env_variable_warning('MISSING_ENV_VAR'))
        self.assertEqual(check_env_variable_warning('TELEGRAM_BOT_TOKEN'), 'dummy_token')

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=False)
    def test_initialize_csv_creates_new(self, mock_exists, mock_open_func):
        initialize_csv('test.csv')
        mock_open_func.assert_called_once_with('test.csv', 'w')

    @patch('requests.post')
    def test_send_telegram_message_success(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        send_telegram_message('dummy_token', 'dummy_chat_id', 'Test Message')
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_send_telegram_message_failure(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.status_code = 400
        send_telegram_message('dummy_token', 'dummy_chat_id', 'Test Message')
        
        # Expecting logging of an error message
        with self.assertLogs(level='ERROR') as log:
            send_telegram_message('dummy_token', 'dummy_chat_id', 'Test Message')
            self.assertIn('❌ Failed to send Telegram message.', log.output[0])

    @patch('generate_article.OpenAI')
    @patch('builtins.open', new_callable=mock_open)
    @patch('generate_article.send_telegram_message')
    def test_get_topics_create_csv_and_notify(self, mock_send_telegram, mock_file, mock_OpenAI):
        # Mocking OpenAI API client
        mock_client = MagicMock()
        mock_OpenAI.return_value = mock_client
        
        # Define a sample response as expected from the OpenAI API
        mock_response = MagicMock()
        mock_response.choices[0].message.content = (
            "Understanding Mineral Veins, Learn about the formation and economic significance of mineral veins in geological structures\n"
            "Gemstones and Their Origins, Explore how different gemstones are formed and the geographical regions where they are found\n"
            "Mining Innovations Today, Discover the latest technological advancements in the mining industry and their impact on efficiency and safety\n"
            "The Beauty of Raw Gems, Examine the natural aesthetics of raw gemstones and their unique appeal in modern jewelry design\n"
            "Sustainable Gemstone Sources, Understand the importance of ethically sourced gemstones and the efforts to ensure environmental sustainability\n"
            "Gold Through the Ages, Delve into the historical significance of gold and its evolving role in economy and culture\n"
            "Crystal Healing Myths, Evaluate the science and beliefs behind crystals and their purported healing properties\n"
            "Artisan Jewelers Stories, Explore how independent jewelers are creating unique pieces with personal and cultural narratives\n"
            "Future of Mineral Exploration, Look at emerging trends in the exploration of minerals with a focus on sustainability\n"
            "The Science of Gem Cutting, Learn about the precision and artistry involved in cutting gemstones to enhance their beauty and value"
        )
        
        # Set the return value of the API client's call
        mock_client.chat.completions.create.return_value = mock_response

        # Call the function under test
        topics = get_topics_create_csv_and_notify(
            api_key='fake_api_key',
            file_path='fake_file_path.csv',
            bot_token='fake_bot_token',
            chat_id='fake_chat_id'
        )

        # Assert that the file was opened correctly
        mock_file.assert_called_once_with('fake_file_path.csv', 'a')

        # Verify content written to file
        mock_file().write.assert_any_call('Understanding Mineral Veins,L')
        self.assertIn("Understanding Mineral Veins", topics)

        # Ensure the send_telegram_message function was called
        mock_send_telegram.assert_called_once_with(
            'fake_bot_token',
            'fake_chat_id',
            "New 10 topics have been generated and saved."
        )

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()


# following code is for manual testing purposes

    """
    #TESTING THE TOPICS GENERATION 
    logging.info("🔄 TESTING CREATE TOPICS...")
    get_topics_create_csv_and_notify(
        OPENAI_API_KEY,
        FILE_PATH_NEW_TOPICS,
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID
    )
    """

    """# Test only fetch_topic_and_description
    logging.info("🔄 TESTING fetch_topic_and_description...")

    # Call the function directly
    topic, description, content_type, ID = fetch_topic_and_description()
    
    # Print the fetched topic and description
    print(f"Topic: {topic}")
    print(f"Description: {description}")
    print(f"Content Type: {content_type}")
    print(f"ID: {ID}")"""
    

    """# TESTING CREATION IMAGE
    # Example test inputs
    test_topic_idea = "Errores comunes en radioaficion"
    test_description = "Evita los fallos tipicos al iniciar tu camino en la radioaficion"

    logging.info("🔄 TESTING get_image_create_file_and_notify...")

    image_path = get_image_create_file_and_notify(test_topic_idea, test_description)

    if image_path:
        print(f"Image generated and saved at: {image_path}")
        logging.info(f"✅ Image generated and saved at: {image_path}")
    else:
        print("Image generation failed.")
        logging.error("❌ Image generation failed.")

    logging.info("✅ Test completed.")"""

    """# TEST GENERATE ALT FOR AN IMAGE
    # Example test inputs
    test_topic_idea = "Errores comunes en radioaficion"
    test_description = "Evita los fallos tipicos al iniciar tu camino en la radioaficion"
    test_image_path = "assets/images/2025-06-21-21-15_Errores_comunes_en_radioaficion.png"  

    logging.info("🔄 TESTING generate_image_alt_text...")

    alt_text = generate_image_alt_text(test_topic_idea, test_description, test_image_path)

    print(f"Generated alt text: {alt_text}")
    logging.info(f"✅ Generated alt text: {alt_text}")"""


    """
    # TESTING THE CREATION OF ARTICLE
    # Example test inputs
    test_topic_idea = "Errores comunes en radioaficion"
    test_description = "Evita los fallos tipicos al iniciar tu camino en la radioaficion"
    test_image_path = "assets/images/2025-06-21-21-15_Errores_comunes_en_radioaficion.png"  
    test_content_type = "article"  
    test_ID = None  

    logging.info("🔄 TESTING get_article_content...")

    article_path = get_article_content(test_topic_idea, test_description, test_image_path, test_content_type, test_ID)

    if article_path:
        print(f"Article generated and saved at: {article_path}")
        logging.info(f"✅ Article generated and saved at: {article_path}")
    else:
        print("Article generation failed.")
        logging.error("❌ Article generation failed.")
    """


