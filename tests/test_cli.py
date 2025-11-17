"""
Tests for the CLI module.

This module tests the command-line interface functionality including
argument parsing, user input, and output formatting.
"""

import pytest
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from src.cli import (
    create_parser,
    load_config,
    get_user_brief_interactive,
    print_brand_names,
    save_json_output,
    run_name_generator_only
)


class TestCreateParser:
    """Test the create_parser function."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None
        assert 'AI Brand Studio' in parser.description

    def test_parser_product_argument(self):
        """Test --product argument parsing."""
        parser = create_parser()
        args = parser.parse_args(['--product', 'Test Product'])
        assert args.product == 'Test Product'

    def test_parser_audience_argument(self):
        """Test --audience argument parsing."""
        parser = create_parser()
        args = parser.parse_args(['--audience', 'Test Audience'])
        assert args.audience == 'Test Audience'

    def test_parser_personality_argument(self):
        """Test --personality argument with valid choices."""
        parser = create_parser()

        # Test valid personalities
        for personality in ['playful', 'professional', 'innovative', 'luxury']:
            args = parser.parse_args(['--personality', personality])
            assert args.personality == personality

    def test_parser_personality_default(self):
        """Test default personality value."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.personality == 'professional'

    def test_parser_count_argument(self):
        """Test --count argument parsing."""
        parser = create_parser()
        args = parser.parse_args(['--count', '25'])
        assert args.count == 25

    def test_parser_verbose_flag(self):
        """Test --verbose flag."""
        parser = create_parser()
        args = parser.parse_args(['--verbose'])
        assert args.verbose is True

        args = parser.parse_args([])
        assert args.verbose is False

    def test_parser_json_argument(self):
        """Test --json output file argument."""
        parser = create_parser()
        args = parser.parse_args(['--json', 'output.json'])
        assert args.json == 'output.json'

    def test_parser_quiet_flag(self):
        """Test --quiet flag."""
        parser = create_parser()
        args = parser.parse_args(['--quiet'])
        assert args.quiet is True


class TestLoadConfig:
    """Test the load_config function."""

    @patch.dict('os.environ', {'GOOGLE_CLOUD_PROJECT': 'test-project'})
    def test_load_config_from_env(self):
        """Test loading config from environment variables."""
        parser = create_parser()
        args = parser.parse_args([])

        config = load_config(args)

        assert config['project_id'] == 'test-project'
        assert config['location'] == 'us-central1'

    @patch.dict('os.environ', {}, clear=True)
    def test_load_config_from_args(self):
        """Test loading config from command-line arguments."""
        parser = create_parser()
        args = parser.parse_args([
            '--project-id', 'cli-project',
            '--location', 'us-west1'
        ])

        config = load_config(args)

        assert config['project_id'] == 'cli-project'
        assert config['location'] == 'us-west1'

    @patch.dict('os.environ', {}, clear=True)
    def test_load_config_missing_project_id(self):
        """Test error when project ID is missing."""
        parser = create_parser()
        args = parser.parse_args([])

        with pytest.raises(ValueError) as exc_info:
            load_config(args)

        assert 'project ID is required' in str(exc_info.value)


class TestGetUserBriefInteractive:
    """Test the get_user_brief_interactive function."""

    @patch('builtins.input')
    def test_interactive_brief_minimal(self, mock_input):
        """Test interactive mode with minimal inputs."""
        # Mock user inputs
        mock_input.side_effect = [
            'Test Product',  # product description
            '',              # audience (optional)
            '',              # personality (default)
            '',              # industry (default)
            ''               # count (default)
        ]

        brief = get_user_brief_interactive()

        assert brief['product_description'] == 'Test Product'
        assert brief['target_audience'] == ''
        assert brief['brand_personality'] == 'professional'
        assert brief['industry'] == 'general'
        assert brief['count'] == 30

    @patch('builtins.input')
    def test_interactive_brief_complete(self, mock_input):
        """Test interactive mode with all inputs."""
        # Mock user inputs
        mock_input.side_effect = [
            'AI Meal Planning App',  # product
            'Busy Parents',          # audience
            '1',                     # personality (playful)
            'food_tech',             # industry
            '40'                     # count
        ]

        brief = get_user_brief_interactive()

        assert brief['product_description'] == 'AI Meal Planning App'
        assert brief['target_audience'] == 'Busy Parents'
        assert brief['brand_personality'] == 'playful'
        assert brief['industry'] == 'food_tech'
        assert brief['count'] == 40

    @patch('builtins.input')
    def test_interactive_brief_retry_empty_product(self, mock_input):
        """Test that empty product description is retried."""
        # Mock user inputs (first empty, then valid)
        mock_input.side_effect = [
            '',              # product (empty - invalid)
            'Valid Product', # product (retry - valid)
            '',              # audience
            '2',             # personality
            '',              # industry
            ''               # count
        ]

        brief = get_user_brief_interactive()

        assert brief['product_description'] == 'Valid Product'

    @patch('builtins.input')
    def test_interactive_brief_invalid_count(self, mock_input):
        """Test handling of invalid count input."""
        # Mock user inputs
        mock_input.side_effect = [
            'Test Product',  # product
            '',              # audience
            '',              # personality
            '',              # industry
            'invalid',       # count (invalid)
            '100',           # count (too high)
            '25'             # count (valid)
        ]

        brief = get_user_brief_interactive()

        assert brief['count'] == 25


class TestPrintBrandNames:
    """Test the print_brand_names function."""

    def test_print_brand_names_normal(self, capsys):
        """Test normal formatted output."""
        names = [
            {
                'brand_name': 'TestBrand',
                'naming_strategy': 'portmanteau',
                'rationale': 'Test rationale',
                'tagline': 'Test tagline',
                'syllables': 2,
                'memorable_score': 8
            }
        ]

        print_brand_names(names, quiet=False, verbose=False)

        captured = capsys.readouterr()
        assert 'TestBrand' in captured.out
        assert 'Test rationale' in captured.out
        assert 'Test tagline' in captured.out

    def test_print_brand_names_quiet(self, capsys):
        """Test quiet mode output."""
        names = [
            {
                'brand_name': 'TestBrand',
                'naming_strategy': 'portmanteau',
                'rationale': 'Test rationale',
                'tagline': 'Test tagline',
                'syllables': 2,
                'memorable_score': 8
            }
        ]

        print_brand_names(names, quiet=True, verbose=False)

        captured = capsys.readouterr()
        assert 'TestBrand' in captured.out
        assert 'Test rationale' not in captured.out
        assert 'Test tagline' not in captured.out

    def test_print_brand_names_verbose(self, capsys):
        """Test verbose mode output."""
        names = [
            {
                'brand_name': 'TestBrand',
                'naming_strategy': 'portmanteau',
                'rationale': 'Test rationale',
                'tagline': 'Test tagline',
                'syllables': 2,
                'memorable_score': 8
            }
        ]

        print_brand_names(names, quiet=False, verbose=True)

        captured = capsys.readouterr()
        assert 'TestBrand' in captured.out
        assert 'portmanteau' in captured.out
        assert 'Syllables: 2' in captured.out
        assert 'Memorable Score: 8' in captured.out

    def test_print_brand_names_empty(self, capsys):
        """Test output with no names."""
        print_brand_names([], quiet=False, verbose=False)

        captured = capsys.readouterr()
        assert 'No brand names generated' in captured.out


class TestSaveJsonOutput:
    """Test the save_json_output function."""

    def test_save_json_success(self):
        """Test successful JSON file save."""
        data = {'test': 'data', 'count': 123}

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name

        try:
            save_json_output(data, temp_path, verbose=False)

            # Verify file was created and contains correct data
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)

            assert loaded_data == data
        finally:
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_save_json_verbose(self, capsys):
        """Test JSON save with verbose output."""
        data = {'test': 'data'}

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name

        try:
            save_json_output(data, temp_path, verbose=True)

            captured = capsys.readouterr()
            assert 'Results saved to' in captured.out
        finally:
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestRunNameGeneratorOnly:
    """Test the run_name_generator_only function."""

    @patch('src.cli.NameGeneratorAgent')
    def test_run_name_generator(self, mock_agent_class):
        """Test running name generator directly."""
        # Mock the agent and its generate_names method
        mock_agent = Mock()
        mock_agent.generate_names.return_value = [
            {'brand_name': 'TestBrand1'},
            {'brand_name': 'TestBrand2'}
        ]
        mock_agent_class.return_value = mock_agent

        config = {'project_id': 'test-project', 'location': 'us-central1'}
        brief = {
            'product_description': 'Test Product',
            'target_audience': 'Test Audience',
            'brand_personality': 'professional',
            'industry': 'general',
            'count': 30
        }

        names = run_name_generator_only(config, brief, verbose=False)

        # Verify agent was initialized
        mock_agent_class.assert_called_once_with(
            project_id='test-project',
            location='us-central1'
        )

        # Verify generate_names was called
        mock_agent.generate_names.assert_called_once()

        # Verify results
        assert len(names) == 2
        assert names[0]['brand_name'] == 'TestBrand1'


class TestEndToEndWorkflow:
    """Test end-to-end CLI workflow."""

    @patch('src.cli.NameGeneratorAgent')
    @patch.dict('os.environ', {'GOOGLE_CLOUD_PROJECT': 'test-project'})
    def test_cli_with_direct_input(self, mock_agent_class):
        """Test CLI with direct command-line input."""
        # Mock the agent
        mock_agent = Mock()
        mock_agent.generate_names.return_value = [
            {
                'brand_name': 'TestBrand',
                'naming_strategy': 'invented',
                'rationale': 'Test rationale',
                'tagline': 'Test tagline',
                'syllables': 2,
                'memorable_score': 8
            }
        ]
        mock_agent_class.return_value = mock_agent

        from src.cli import main, create_parser, load_config, run_name_generator_only

        parser = create_parser()
        args = parser.parse_args([
            '--product', 'Test Product',
            '--personality', 'playful',
            '--count', '25',
            '--quiet'
        ])

        config = load_config(args)
        brief = {
            'product_description': args.product,
            'target_audience': args.audience,
            'brand_personality': args.personality,
            'industry': args.industry,
            'count': args.count
        }

        names = run_name_generator_only(config, brief, verbose=False)

        assert len(names) == 1
        assert names[0]['brand_name'] == 'TestBrand'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
