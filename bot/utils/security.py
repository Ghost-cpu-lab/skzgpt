"""
Utilitários de segurança
"""
import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Validador de segurança para entradas do usuário"""
    
    def __init__(self):
        # Palavras/padrões bloqueados (adicione conforme necessário)
        self.blocked_patterns = [
            r'@everyone',
            r'@here',
            r'discord\.gg/',
            r'https?://discord\.gg/',
        ]
        
        # Limite de tamanho de mensagem
        self.max_message_length = 2000
        
        logger.info("✅ Validador de segurança inicializado")
    
    def validate_input(self, text: str) -> bool:
        """
        Valida entrada do usuário
        """
        if not text or not text.strip():
            return False
        
        # Verificar tamanho
        if len(text) > self.max_message_length:
            logger.warning(f"⚠️ Mensagem muito longa: {len(text)} caracteres")
            return False
        
        # Verificar padrões bloqueados
        text_lower = text.lower()
        for pattern in self.blocked_patterns:
            if re.search(pattern, text_lower):
                logger.warning(f"⚠️ Padrão bloqueado detectado: {pattern}")
                return False
        
        return True
    
    def sanitize_text(self, text: str) -> str:
        """
        Limpa texto removendo caracteres perigosos
        """
        if not text:
            return ""
        
        # Remover mentions everyone/here
        text = re.sub(r'@(everyone|here)', '@\\1', text, flags=re.IGNORECASE)
        
        # Limitar tamanho
        if len(text) > self.max_message_length:
            text = text[:self.max_message_length-3] + "..."
        
        return text.strip()
    
    def is_admin_command(self, text: str) -> bool:
        """
        Verifica se o texto contém comandos administrativos
        """
        admin_keywords = [
            'criar canal', 'deletar canal', 'criar cargo', 'deletar cargo',
            'limpar mensagem', 'ban', 'kick', 'mute', 'embed'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in admin_keywords)