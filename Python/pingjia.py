# coding: UTF-8
import urllib
import urllib2
import re
from pyquery import PyQuery as pq
from lxml import etree
import os
import string
import StringIO
username=""
password=""
host="http://221.218.249.116/"
session=""
name=""
aspxsession=""
courselist=[]
loginpage="default5.aspx"
gnmkdm=None
#urllib函数，用于提交http数据
def open(aurl,post='',Referer=''):
    #proxy = 'http://127.0.0.1:8088'
    #opener = urllib2.build_opener( urllib2.ProxyHandler({'http':proxy}) )
    #urllib2.install_opener(opener)
    if post!='':
        test_data_urlencode = urllib.urlencode(post)
        req = urllib2.Request(url=aurl,data = test_data_urlencode)
    else:
        req = urllib2.Request(url=aurl)
    if Referer!='':
        req.add_header('Referer',Referer)
    if aspxsession!="":
        req.add_header('Cookie',aspxsession)
    res_data = urllib2.urlopen(req)
    return res_data
#获得正方教务系统session
def getsession():
    try:
        global session,hosturl,aspxsession
        openres=urllib2.urlopen(urllib2.Request(url = host))
        openurl=openres.geturl()
        if ")" in openurl and "(" in openurl:
            mylist= re.findall(r"(?<=\().*?(?=\))",openurl,re.DOTALL)
            session= mylist[0]
            print u"成功获取session:"+session
            hosturl=host+'('+session+')/'
        else:
            hosturl=host
            print u"服务器连接正常"
            aspxsession = re.findall(r"^.*?(?=; path=/)",openres.info().getheader('Set-Cookie'),re.DOTALL)[0]
    except:
        return 0
    return 1
#用户登录模块
def login():
    global name,gnmkdm
    res=open(hosturl+loginpage).read().decode('gbk')
    d = pq(res)
    form = d('form')
    fi=form('input')
    ele={}
    for i in range(0,len(fi)-1):
        if fi.eq(i).attr('name')!='RadioButtonList1':
            ele.update({fi.eq(i).attr('name'):fi.eq(i).attr('value')})
        if fi.eq(i).attr('name')=="TextBox3":
            icodeurl="CheckCode.aspx"
            icoderes=open(hosturl+icodeurl).read()
            from PIL import Image
            img = Image.open(StringIO.StringIO(icoderes))
            img = img.convert('RGB')
            img.save(username+"icode.jpeg")
            os.system("jp2a "+username+"icode.jpeg -b -i --colors --chars=' *'")
            icode=raw_input("请输入验证码:")
            ele.update({fi.eq(i).attr('name'):icode})
    ele.update({'TextBox1': username, 'TextBox2': password, 'ddl_js':u'学生'.encode('gbk'), 'Button1':u" 登 录 ".encode('gbk')})
    res = open(hosturl+loginpage,ele).read().decode('gbk')
    if "xs_main.aspx" in res:
        print u"登录成功"
        res=open(hosturl+"xs_main.aspx?xh="+username).read().decode('gbk')
        d = pq(res)
        print d('#xhxm').text()
        name = re.findall(u".*?(?=同学)",d('#xhxm').text(),re.DOTALL)[0]
        print u"用户名："+name
        '''
        try:
        	gnmkdm = re.findall(u"(?<=xf_xsqxxxk.aspx\?xh="+username+"\&xm="+name+"\&gnmkdm=).*?(?=\")",res,re.DOTALL)[0]
        except:
        	print u"没有找到选课界面"
        	exit()
        '''
        return 1
    elif u"密码错误" in res:
        print u"密码错误!"
        init()
        return login()
    elif u"用户名不存在" in res:
        print u"用户名不存在或未按照要求参加教学活动"
        init()
        return login()
    else:
        return 0
#从主页面中获取课程数据
def getcourselist():
    global courselist,gnmkdm
    url=hosturl+"xs_main.aspx?xh="+username
    d = pq(url)
    span=d(u".top_link span")
    flag=False
    for i in range(0,len(span)):
        if span[i].text == u' 教学质量评价':
            span = span.eq(i)
            flag=True
            break;
    if flag==False:
        print u'没有找到评价页面'
        exit()
    toplink = span.parent()
    ul = toplink.next().next().next()
    li = ul('li')
    if len(li)==0:
        print u'没有可评价的课程'
        exit()

    for i in range(0,len(li)):
        ahref = li.eq(i).find('a').attr('href')
        if gnmkdm is None:
            gnmkdm = re.findall(u"(?<=&gnmkdm=).*",ahref,re.DOTALL)[0]
        #kh = re.findall(u"(?<=xkkh=).*?(?=&)",ahref,re.DOTALL)[0]
        courselist.append(ahref)

    '''
    tr=table('tr:not(.datelisthead)')
    ele={}
    for i in range(0,len(tr)):
        td=tr.eq(i)('td')
        xkbtname=td.eq(0)('input').attr('name')
        xsbtname=td.eq(1)('input').eq(0).attr('name')
        xsvalue=td.eq(1)('input').eq(1).attr('value')
        name=td.eq(2)('a').text()
        code=td.eq(3).text()
        teacher=td.eq(4)('a').text()
        time=td.eq(5).attr('title')
        if time == None:
            time=""
        place=td.eq(6).text()
        if place == None:
            place=""
        credit=td.eq(7).text()
        ele.update({i+1:{'xkbtname':xkbtname,'xsbtname':xsbtname,'xsvalue':xsvalue,'name':name,'code':code,'teacher':teacher,'time':time,'place':place,'credit':credit,}})
    classlist = ele
    '''
#获得页面表单值
def getele(res):
    d = pq(res)
    form = d('form')
    fi=form('input')
    ele={}
    for i in range(0,len(fi)):
        if fi.eq(i).attr('type') == 'submit' or (fi.eq(i).attr('value') ==None and fi.eq(i).attr('type')!="text") or fi.eq(i).attr('type') == 'button':
            continue
        if fi.eq(i).attr('value')==None:
            vvalue=""
        else:
            vvalue=fi.eq(i).attr('value').encode('gbk')
        ele.update({fi.eq(i).attr('name'):vvalue})
    fi=form('select')
    for i in range(0,len(fi)):
        if fi.eq(i)('option:selected').attr('value') is None:
            vvalue=''
        else:
            vvalue=fi.eq(i)('option:selected').attr('value').encode('gbk')
        ele.update({fi.eq(i).attr('name'):vvalue})
    return ele
def pingjia():
    for c in courselist:
        res = open(hosturl+c,'',hosturl+c).read().decode('gbk')
        p = pq(res)
        ele = getele(res)
        isfirstlist=[]
        for e in ele:
            if e[:8]=='DataGrid':
                if e[:9] not in isfirstlist:
                    ele[e]=u'比较符合'.encode('gbk')
                    isfirstlist.append(e[:9])
                else:
                    ele[e]=u'非常符合'.encode('gbk')
        ele.update({'Button1':u'保  存'.encode('gbk')})
        res = open(hosturl+c,ele,hosturl+c).read().decode('gbk')

def submitpingjia():
    c = courselist[0]
    res = open(hosturl+c,'',hosturl+c).read().decode('gbk')
    p = pq(res)
    ele = getele(res)
    ele.update({'Button2':u' 提  交 '.encode('gbk')})
    res = open(hosturl+c,ele,hosturl+c).read().decode('gbk')
#程序初始化登录函数
def init():
    global username,password
    username=raw_input("用户名:")
    password=raw_input("密  码:")
#程序开始
if __name__ == '__main__':
    init()
    while not getsession():
        print u"session获取失败，正在重试"
    while not login():
        print u"登录失败，正在重试"
    getcourselist()
    pingjia()
    submitpingjia()
    print u"您已完成评价,共评价%d节课程，感谢使用"%(len(courselist))
