# 2020-12-05 创建该文件
class PageInfo(object):
    def __init__(self, current_page, all_count, per_page, show_page, page_url, key, keyname):
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
        self.key = key
        self.keyname = keyname

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

        # 首页设置
        first = "<a style='float: left;color: #880010' href='%s?%s=%s&page=%s'>&nbsp;&nbsp;首页&nbsp;|&nbsp;</a>" % (self.page_url, self.keyname, self.key, 1)
        page_list.append(first)

        # 上一页的设置
        if self.current_page <=1:
            pre = "<a style='float: left;color: #880001' href='%s?%s=%s&page=%s'>上一页</a>" % (self.page_url, self.keyname, self.key, 1)
        else:
            pre  = "<a style='float: left;color: #880001' href='%s?%s=%s&page=%s'>上一页</a>" % (self.page_url, self.keyname, self.key, self.current_page-1)
        page_list.append(pre)

        for i in range(begin, stop):
            if i == self.current_page:
                temp = "<a style='color: #DC143C;display:inline-black;padding:5px;margin:5p;'" \
                       "href='%s?%s=%s&page=%s'><b>%s</b></a>" % (self.page_url, self.keyname, self.key, i, i,)
            else:
                temp = "<a style='display:inline-black;padding:5px;margin:5p;' " \
                       "href='%s?%s=%s&page=%s'>%s</a>" % (self.page_url, self.keyname, self.key, i, i,)
            page_list.append(temp)

        # 下一页的设置
        if self.current_page >= self.all_pager:
            nex = "<a style='color: #880001' href='%s?%s=%s&&page=%s'>下一页</a>" % (self.page_url, self.keyname, self.key,self.all_pager)
        else:
            nex = "<a style='color: #880001' href='%s?%s=%s&page=%s'>下一页</a>" % (self.page_url,  self.keyname, self.key, self.current_page+1)
        page_list.append(nex)

        # 尾页设置
        end = "<a style='color: #880010' href='%s?%s=%s&page=%s'>&nbsp;|&nbsp;尾页</a>" % (self.page_url, self.keyname, self.key, self.all_pager)
        page_list.append(end)

        # 总页数统计
        count = "<font color='#880010'>&nbsp;&nbsp;&nbsp;&nbsp;共&nbsp;<font color = '#a52a2a'><b>%s</b></font>&nbsp;页</font>" % (self.all_pager)
        page_list.append(count)

        return ''.join(page_list)