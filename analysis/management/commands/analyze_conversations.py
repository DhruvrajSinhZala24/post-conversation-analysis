"""
Management command to manually trigger analysis on conversations.
Usage: python manage.py analyze_conversations [--all]
"""
from django.core.management.base import BaseCommand
from analysis.models import Conversation, ConversationAnalysis
from analysis.analyzer import ConversationAnalyzer


class Command(BaseCommand):
    help = 'Analyze conversations (unanalyzed by default, use --all for all)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Analyze all conversations, including already analyzed ones',
        )
        parser.add_argument(
            '--conversation-id',
            type=int,
            help='Analyze a specific conversation by ID',
        )

    def handle(self, *args, **options):
        analyzer = ConversationAnalyzer()
        
        if options['conversation_id']:
            try:
                conversation = Conversation.objects.get(id=options['conversation_id'])
                conversations = [conversation]
            except Conversation.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Conversation {options["conversation_id"]} not found')
                )
                return
        elif options['all']:
            conversations = Conversation.objects.all()
        else:
            conversations = Conversation.objects.filter(analyzed=False)
        
        analyzed_count = 0
        
        for conversation in conversations:
            messages = [
                {'sender': msg.sender, 'message': msg.text}
                for msg in conversation.messages.all()
            ]
            
            if not messages:
                self.stdout.write(
                    self.style.WARNING(f'Conversation {conversation.id} has no messages, skipping...')
                )
                continue
            
            # Perform analysis
            analysis_data = analyzer.analyze(messages)
            
            # Create or update analysis
            ConversationAnalysis.objects.update_or_create(
                conversation=conversation,
                defaults=analysis_data
            )
            
            # Mark as analyzed
            conversation.analyzed = True
            conversation.save()
            
            analyzed_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Analyzed conversation {conversation.id} - Overall Score: {analysis_data["overall_score"]:.2f}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nCompleted: Analyzed {analyzed_count} conversation(s).')
        )

