from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey


class movie(models.Model):
    id = models.AutoField(primary_key=True,verbose_name="编号")
    name = models.CharField(max_length=255,verbose_name="名称")
    rate = models.FloatField(null=False,default=0,verbose_name="平均评分")
    rate_num = models.IntegerField(null=False,default=0,verbose_name="评分人数")
    comment_num = models.IntegerField(null=False,default=0,verbose_name="评论人数")
    type = models.CharField(max_length=255,verbose_name="类型")
    director = models.TextField(max_length=65535,verbose_name="导演")
    writer = models.TextField(max_length=65535,verbose_name="编剧")
    actor = models.TextField(max_length=65535,verbose_name="演员")
    area = models.CharField(max_length=255,verbose_name="地区")
    language = models.CharField(max_length=255,verbose_name="语言")
    date = models.DateField(verbose_name="日期")
    time = models.IntegerField(null=False,default=0,verbose_name="时长")
    intro = models.TextField(max_length=65535,verbose_name="简介")
    class Meta:
        db_table = 'movie'
        verbose_name = u'电影'

    def __str__(self):
        return "《%s》" % self.name



class user(AbstractUser):
    class Meta:
        db_table = 'user'
        verbose_name = u'用户'

    def __str__(self):
        return self.username

class rate(models.Model):
    id = models.AutoField(primary_key=True,verbose_name="编号")
    # uid = models.IntegerField(null=False,verbose_name="用户编号")
    uid = models.ForeignKey(user,on_delete=models.CASCADE,verbose_name="用户",related_name="rate_user")
    #movie_id=models.IntegerField(null=False,verbose_name="电影编号")
    movie_id = models.ForeignKey(movie,on_delete=models.CASCADE,verbose_name="电影",related_name="rate_movie")
    time = models.DateTimeField(null=False,verbose_name="评分时间")
    rate = models.IntegerField(null=False,default=0,verbose_name="评分")
    class Meta:
        db_table = 'rate'
        verbose_name = u'评分'

class comment(models.Model):
    id = models.AutoField(primary_key=True,verbose_name="编号")
    # uid = models.IntegerField(null=False,verbose_name="用户编号")
    uid = models.ForeignKey(user, on_delete=models.CASCADE, verbose_name="用户", related_name="comment_user")
    #movie_id = models.IntegerField(null=False,verbose_name="电影编号")
    movie_id = models.ForeignKey(movie, on_delete=models.CASCADE, verbose_name="电影",related_name="comment_movie")
    time = models.DateTimeField(null=False,verbose_name="评论时间")
    rate = models.IntegerField(default=0,verbose_name="评分")
    comment = models.TextField(max_length=65535,verbose_name="评论")
    favor_num = models.IntegerField(default=0,verbose_name="点赞人数")
    oppo_num = models.IntegerField(default=0,verbose_name="点踩人数")
    class Meta:
        db_table = 'comment'
        verbose_name = u'评论'


class recommendion(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.ForeignKey(user, on_delete=models.CASCADE, verbose_name="用户", related_name="recommend_user")
    mv1 = models.ForeignKey(movie,on_delete=models.CASCADE,verbose_name="推荐1",related_name="recommend_mv1")
    mv2 = models.ForeignKey(movie,on_delete=models.CASCADE,verbose_name="推荐2",related_name="recommend_mv2")
    mv3 = models.ForeignKey(movie,on_delete=models.CASCADE,verbose_name="推荐3",related_name="recommend_mv3")
    mv4 = models.ForeignKey(movie,on_delete=models.CASCADE,verbose_name="推荐4",related_name="recommend_mv4")
    mv5 = models.ForeignKey(movie, on_delete=models.CASCADE, verbose_name="推荐5", related_name="recommend_mv5")
    mv6 = models.ForeignKey(movie, on_delete=models.CASCADE, verbose_name="推荐6", related_name="recommend_mv6")
    mv7 = models.ForeignKey(movie, on_delete=models.CASCADE, verbose_name="推荐7", related_name="recommend_mv7")
    mv8 = models.ForeignKey(movie, on_delete=models.CASCADE, verbose_name="推荐8", related_name="recommend_mv8")
    mv9 = models.ForeignKey(movie, on_delete=models.CASCADE, verbose_name="推荐9", related_name="recommend_mv9")
    mv10 = models.ForeignKey(movie, on_delete=models.CASCADE, verbose_name="推荐10", related_name="recommend_mv10")
    mv11 = models.ForeignKey(movie, on_delete=models.CASCADE, verbose_name="推荐11", related_name="recommend_mv11")
    mv12 = models.ForeignKey(movie, on_delete=models.CASCADE, verbose_name="推荐12", related_name="recommend_mv12")
    class Meta:
        db_table = 'recommendation'
        verbose_name = u'推荐列表'



class blog(models.Model):
    id = models.AutoField(primary_key=True,verbose_name="编号")
    author = models.ForeignKey(user,on_delete=models.CASCADE,verbose_name="作者")
    title = models.CharField(max_length=255,verbose_name="标题")
    movie = models.ForeignKey(movie,on_delete=models.CASCADE,verbose_name="电影")
    body = models.TextField(verbose_name="内容")
    create_time = models.DateTimeField(default=timezone.now,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True,verbose_name="更新时间")
    class Meta:
        db_table = 'blog'
        verbose_name = u'影评'


class blogComment(MPTTModel):
    id = models.AutoField(primary_key=True,verbose_name="编号")
    article = models.ForeignKey(blog,on_delete=models.CASCADE,verbose_name="博客",related_name="blogcomment_blog")
    reply = models.ForeignKey(user, on_delete=models.CASCADE, verbose_name="评论人",related_name="blogcomment_reply")
    reply_to = models.ForeignKey(user, on_delete=models.CASCADE, verbose_name="被评论人",related_name="blogcomment_replyto")
    content = models.TextField(verbose_name="评论内容")
    create_time = models.DateTimeField(default=timezone.now,verbose_name="创建时间")
    parent = TreeForeignKey('self',null=True,blank=True,on_delete=models.CASCADE,related_name='blogcomment_parent',verbose_name='父级')
    class Meta:
        db_table = 'blogComment'
        verbose_name = u'影评评论'

