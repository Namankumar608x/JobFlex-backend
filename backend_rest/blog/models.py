from django.db import models
from user.models import User

class Blog(models.Model):
    id = models.AutoField(primary_key=True)
    U_ID = models.ForeignKey(User, on_delete=models.CASCADE, db_column='U_ID')
    title = models.CharField(max_length=255)
    blogtext = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'blog'

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    U_ID = models.ForeignKey(User, on_delete=models.CASCADE, db_column='U_ID')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment'

    def __str__(self):
        return f"Comment by {self.U_ID} on {self.blog}"
 
class Upvote(models.Model):
    id = models.AutoField(primary_key=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='upvotes')
    U_ID = models.ForeignKey(User, on_delete=models.CASCADE, db_column='U_ID')

    class Meta:
        db_table = 'upvote'
        unique_together = ('blog', 'U_ID')#on one blog only one upvote from a user

    def __str__(self):
        return f"Upvote by {self.U_ID} on {self.blog}"