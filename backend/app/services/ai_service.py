import os
import google.generativeai as genai
from typing import Optional
from ..models import KnowledgeBaseItem
from ..schemas import CommentResponse

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the model
model = genai.GenerativeModel("gemini-pro")

class AIService:
    @staticmethod
    def generate_comment(post_content: str, context: Optional[str] = None) -> CommentResponse:
        """
        Generate a relevant comment for a social media post using Gemini AI
        """
        prompt = f"""
        You are an AI assistant helping with professional social media engagement.
        Based on the following post content and context, generate a relevant, professional comment.
        Keep it concise (1-2 sentences max) and appropriate for LinkedIn.
        
        Post Content: {post_content}
        
        {f'Context: {context}' if context else ''}
        """
        
        try:
            response = model.generate_content(prompt)
            return CommentResponse(
                success=True,
                comment=response.text,
                raw_response=response
            )
        except Exception as e:
            return CommentResponse(
                success=False,
                error=str(e)
            )

    @staticmethod
    def generate_comment_with_rag(post_content: str, knowledge_base_items: list[KnowledgeBaseItem]) -> CommentResponse:
        """
        Generate a comment using RAG (Retrieval-Augmented Generation) from knowledge base
        """
        context = "\n".join([item.content for item in knowledge_base_items])
        return AIService.generate_comment(post_content, context)