"""
分页组件使用示例：

    obj = Pagination(request.GET.get('page',1),len(USER_LIST),request.path_info)
    page_user_list = USER_LIST[obj.start:obj.end]
    page_html = obj.page_html()

    return render(request,'index.html',{'users':page_user_list,'page_html':page_html})

"""

class Pagination(object):

    def __init__(self,current_page_num,all_count,request,per_page_num=2,pager_count=11):
        """
        封装分页相关数据
        :param current_page_num: 当前访问页的数字
        :param all_count:    分页数据中的数据总条数
        :param per_page_num: 每页显示的数据条数
        :param pager_count:  最多显示的页码个数
        """
        try:
            current_page_num = int(current_page_num)
        except Exception as e:
            current_page_num = 1

        if current_page_num <1:
            current_page_num = 1

        self.current_page_num = current_page_num

        self.all_count = all_count
        self.per_page_num = per_page_num

        # 实际总页码
        all_pager, tmp = divmod(all_count, per_page_num)
        if tmp:
            all_pager += 1
        self.all_pager = all_pager


        self.pager_count = pager_count
        self.pager_count_half = int((pager_count - 1) / 2)  # 5


        # 保存搜索条件

        import copy
        self.params=copy.deepcopy(request.GET) # {"a":"1","b":"2"}

    @property
    def start(self):
        return (self.current_page_num - 1) * self.per_page_num

    @property
    def end(self):
        return self.current_page_num * self.per_page_num

    def page_html(self):
        # 如果总页码 < 11个：
        if self.all_pager <= self.pager_count:
            pager_start = 1
            pager_end = self.all_pager + 1
        # 总页码  > 11
        else:
            # 当前页如果<=页面上最多显示11/2个页码
            if self.current_page_num <= self.pager_count_half:
                pager_start = 1
                pager_end = self.pager_count + 1
            # 当前页大于5
            else:
                # 页码翻到最后
                if (self.current_page_num + self.pager_count_half) > self.all_pager:

                    pager_start = self.all_pager - self.pager_count + 1
                    pager_end = self.all_pager + 1

                else:
                    pager_start = self.current_page_num - self.pager_count_half
                    pager_end = self.current_page_num + self.pager_count_half + 1

        page_html_list = []
        first_page = '<a href="?page=%s">&lt;&lt;</a>' % (1,)
        page_html_list.append(first_page)

        if self.current_page_num <= 1:
            pass
        else:
            prev_page = '<a href="?page=%s">&lt;</a>' % (self.current_page_num - 1,)

        page_html_list.append(prev_page)


        #self.params=copy.deepcopy(request.GET) # {"a":"1","b":"2"}

        for i in range(pager_start, pager_end):

            self.params["page"]=i

            if i == self.current_page_num:
                temp = '<a href="?%s" class="active">%s</a>' %(self.params.urlencode(),i)
            else:
                temp = '<a href="?%s">%s</a>' % (self.params.urlencode(),i,)
            page_html_list.append(temp)


        if self.current_page_num >= self.all_pager:
            pass
        else:
            next_page = '<a href="?page=%s">&gt;</a>' % (self.current_page_num + 1,)
        page_html_list.append(next_page)
        last_page = '<a href="?page=%s">&gt;&gt;</a>' % (self.all_pager,)
        page_html_list.append(last_page)

        return ''.join(page_html_list)