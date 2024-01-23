import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from random import random
import json
from .ai import minimax, alphabeta

# Configure logging
logger = logging.getLogger(__name__)

DEPTH_EASY = 2
DEPTH_MEDIUM = 4
DEPTH_HARD = 5

@csrf_exempt
def make_move(request):
    try:
        state = json.loads(request.body)
        difficulty = state['difficulty']
        player = state['player']
        line_made = state['line_made']

        if state['black_remaining'] == 9:
            x = int(random() * 2)
            y = int(random() * 2)
            z = int(random() * 2)
            if y == 1 and z == 1:
                z = 2
            move = ['set', -1, x, y, z]
        else:
            if difficulty == 'easy':
                _, move = minimax(state, DEPTH_EASY, player, line_made)
            elif difficulty == 'medium':
                _, move = alphabeta(state, DEPTH_MEDIUM, -100000, 100000, player, line_made)
            elif difficulty == 'hard':
                _, move = alphabeta(state, DEPTH_HARD, -100000, 100000, player, line_made)

        logger.info("Move calculated: %s", move)
        return JsonResponse({ 'move': move })

    except Exception as e:
        logger.error("Error in make_move: %s", e)
        return JsonResponse({'error': 'An error occurred'}, status=500)
