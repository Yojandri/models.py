# 2020-12-05 创建该文件
class PageInfo(object):
    def __init__(self, current_page, all_count, per_page, show_page, page_url):
        # 防止用户传入非数字的值
        try:
            self.current_page = int(current_page)
        except Exception as e:
            self.current_page = 1
        self.per_page = per_page

        a, b = divmod(all_count, per_page)
        if b:
            a = a+1
        self.all_pager = a
        self.show_page = show_page
        self.page_url = page_url

    def start(self):
        return (self.current_page - 1) * self.per_page

    def end(self):
        return self.current_page * self.per_page

    def pager(self):
        page_list = []
        half = int((self.show_page-1)/2)

        if self.all_pager <= self.show_page:
            begin = 1
            stop = self.all_pager + 1
        else:
            # 如果当前页<= 2
            if self.current_page <= half:
                begin = 1
                stop = self.show_page + 1  # 2020-12-05 22:19 修改
            else:
                if self.current_page + half > self.all_pager:
                    begin = self.all_pager - self.show_page + 1
                    stop = self.all_pager + 1
                else:
                    begin = self.current_page - half
                    stop = self.current_page + half + 1

        # 上一页的设置
        if self.current_page <=1:
            pre = "<a style='display:inline-black;padding:5px;margin:5p' href='%s?page=%s'>上一页</a>" % (self.page_url, 1)
        else:
            pre  = "<a style='display:inline-black;padding:5px;margin:5p' href='%s?page=%s'>上一页</a>" % (self.page_url, self.current_page-1)
        page_list.append(pre)

        for i in range(begin, stop):
            if i == self.current_page:
                temp = "<a style='display:inline-black;padding:5px;margin:5p;background-color:red'" \
                       "href='%s?page=%s'>%s</a>" % (self.page_url, i, i,)
            else:
                temp = "<a style='display:inline-black;padding:5px;margin:5p;' " \
                       "href='%s?page=%s'>%s</a>" % (self.page_url, i, i,)
            page_list.append(temp)

        # 下一页的设置
        if self.current_page >= self.all_pager:
            nex = "<a style='display:inline-black;padding:5px;margin:5p' href='%s?page=%s'>下一页</a>" % (self.page_url, self.all_pager)
        else:
            nex  = "<a style='display:inline-black;padding:5px;margin:5p' href='%s?page=%s'>下一页</a>" % (self.page_url, self.current_page+1)
        page_list.append(nex)

        return ''.join(page_list)