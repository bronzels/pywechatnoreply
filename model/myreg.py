# -*- coding: utf-8 -*-
import re
from common.const import *
from model.rbt3_config import sp_words
formed_regs={
    '拉黑':r'被对方拒收了。?$|无法接收消息$|开启了朋友验证.*?才能聊天。?$|^对方未添加你为朋友',
    '招呼':r'^voip_content_(video|voice)(对方|已取消|忙线未接听|连接失败)|^以上是打招呼的内容|拍了拍我$|现在我?们?可以开始聊天了。?$|^我是群聊.*?的.+|^请求添加你为朋友',
    '无意':r'撤回了一条消息$|拍了拍自己$|将此好友从.*?给|^邀请你加入群聊|朋友拍了拍你的头像后会出现设置的内容。?$|^你有一笔待接收的转账|^如果对方使用的不是最新版本微信',
    '通话':r'^voip_content_(video|voice)(聊天时长|通话中断)',
    '红包转账':r'领取了你的红包。?$|^收到转账',
    '拒接':r'^voip_content_voice已拒绝|^voip_content_video已拒绝',
    '提示':r'^发送消息过于频繁|^操作过于频繁|^与对方发生资金往来可能存在风险|^对方帐号异常',
    '企微转友':r'^由于工作变更.*?提供服务。',
    '忽略':r'不[要用]回复|请?[别勿]回复|请忽略',
}


formed_regs_map={
'拉黑':SUB_CLASSIFIER_re_lahei,
"招呼":SUB_CLASSIFIER_re_zhaohu,
"无意":SUB_CLASSIFIER_re_wuyi,
"通话":SUB_CLASSIFIER_re_tonghua,
#"纯媒体":105,
"红包转账":SUB_CLASSIFIER_re_hongbao,
"拒接":SUB_CLASSIFIER_re_jujie,
"TBD":SUB_CLASSIFIER_re_TBD,
"无文本":SUB_CLASSIFIER_re_wuwenben,
"企微转友":SUB_CLASSIFIER_re_qiye,
}


merge_reg={
"无文本":r'^((\[独立表情\]|\[音频\]|\[视频\]|\[图片\]|\[独立链接\]|\[截图\]|\[企微转友\]|\[提示\]|\[红包转账\]|\[无意\]|\[通话\]|);)*(\[独立表情\]|\[音频\]|\[视频\]|\[图片\]|\[独立链接\]|\[截图\]|\[企微转友\]|\[提示\]|\[红包转账\]|\[无意\]|\[通话\]|)$',
}


yes_no_map={
    SUB_CLASSIFIER_xiaoshou:1,
    SUB_CLASSIFIER_guihua:1,
    SUB_CLASSIFIER_shijian:1,
    SUB_CLASSIFIER_gongju:1,
    SUB_CLASSIFIER_jiaoshi:1,
    SUB_CLASSIFIER_huoli:1,
    SUB_CLASSIFIER_shouhou:1,
    SUB_CLASSIFIER_dizhi:1,
    SUB_CLASSIFIER_geren:1,
    SUB_CLASSIFIER_zixun:1,
    SUB_CLASSIFIER_dazhaohu:1,
    SUB_CLASSIFIER_jujue:0,
    SUB_CLASSIFIER_kaolv:0,
    SUB_CLASSIFIER_zantongke:0,
    SUB_CLASSIFIER_zantongbu:0,
    SUB_CLASSIFIER_bangmang:0,
    SUB_CLASSIFIER_jitang:0,
    SUB_CLASSIFIER_ad:0,
    SUB_CLASSIFIER_xianliao:0,
    SUB_CLASSIFIER_qita:0,
    SUB_CLASSIFIER_re_lahei:0,
    SUB_CLASSIFIER_re_zhaohu:1,
    SUB_CLASSIFIER_re_wuyi:0,
    SUB_CLASSIFIER_re_tonghua:0,
    SUB_CLASSIFIER_re_hongbao:0,
    SUB_CLASSIFIER_re_jujie:1,
    SUB_CLASSIFIER_re_qiye:0,
    SUB_CLASSIFIER_re_TBD:0,
    SUB_CLASSIFIER_re_wuwenben:0,
}

pure_text_map={
    '[阿卡索寒暄]':('𝙂𝙤𝙤𝙙 𝙢𝙤𝙧𝙣𝙞𝙣𝙜',0),
    '[上课说明]':('上课教室具有中英互译的功能|已为[您你]预约了英语课程',90),
    '[求回复]':('(回复|扣|发送|回).{0,3}(①|1|学习|我要|风采)',90),
    '[群发声明]':('(群发|打扰).{0,10}(打扰|见谅|谅解|包含|海涵)',20),
}


sub_regs={
    "[网盘地址]": r'链接[:：] ?http.*?提取码[:：] ?[\da-zA-Z]{4}.*?(?:的分享|操作更方便哦)?',
    '[链接]':r'(https?|ftp|file|chrome-extension)://[\*\-A-Za-z0-9+&@#/%?=~_|!:,.;]+[\*\-A-Za-z0-9+&@#/%=~_|]',
    ';':r'\\n|\n|\r\n|\t',
    '"':r"‘|”|“",
    '…':r'⋯',
    '[ok]':'(👌🏻)|👌|👏',
    '[微笑]':'😄|😁|😂|😊|😉|🧐|😳|😘|😜|😃|😍|☺|🤔|😅|😝|😀|🤔|😚|😋',
    '>':r'&gt;',
    '<':r'&lt;',
    '─':r'一',
    '=':r'═',
    '[强]':r'👍',
    '[合十]':r'🙏',
    '[加油]':r'💪',
    '[鼓掌]':r'👏',
    '[爱心]':r'❤|💝|❥|💓',
    '[疑问]':r'❓',
    '[礼物]':r'🎁',
    '[叹气]':r'😔',
    '&':r'&amp;',

}
overlap_reg=r'([\-\…\,\?\!\(\)\.\:\"\~\@\#\%\&\*\;\—\=\═ 哈嗯哦啊一─_。，、\n\t])\1+'#|\[.*?\]
overlap_emoji=r'(\[.*?\])\1+'
no_text_reg=r'^((\[独立表情\]|\[音频\]|\[视频\]|\[图片\]|\[独立链接\]|\[截图\]|\[企微转友\]|\[提示\]|\[红包转账\]|\[无意\]|\[通话\]|);)*(\[独立表情\]|\[音频\]|\[视频\]|\[图片\]|\[独立链接\]|\[截图\]|\[企微转友\]|\[提示\]|\[红包转账\]|\[无意\]|\[通话\]|)$'
none_reg=r'[\u200d\x0b\x01\x02\xa0\u3000\ue312\ue412\ue41d\ue415\ue112\ue327\u202d\ue303]'
senseless_reg=r'^([\s\;\.\,\~\"\'\-。一─═_，…# ])\1+$|^$'
senseless_regs=r'^((\[无意\]|\[提示\]|\[企微转友\]);)*(\[无意\]|\[提示\]|\[企微转友\])$'
emoji_tab = "微笑][撇嘴][色][发呆][得意][流泪][害羞][闭嘴][睡][大哭][尴尬][发怒][调皮][呲牙][惊讶][难过][囧][抓狂][吐][偷笑][愉快][白眼][傲慢][困][惊恐][憨笑][悠闲][奋斗][咒骂][疑问][嘘][晕][骷髅][衰][敲打][再见] [擦汗][抠鼻][鼓掌][坏笑][右哼哼][哈欠][鄙视][委屈] [快哭了][阴险][亲亲][可怜][笑脸][生病][脸红][破涕为笑][恐惧][失望][无语][嘿哈][捂脸][奸笑][机智][皱眉][耶][吃瓜][加油][汗][天啊][Emm][社会社会][旺财][好的][打脸][哇][翻白眼][666][让我看看][叹气][苦涩][裂开][嘴唇][爱心][心碎][拥抱][强][弱][握手][胜利][抱拳][勾引][拳头][OK][合十][啤酒][咖啡][蛋糕][玫瑰][凋谢][菜刀][炸弹][便便][月亮][太阳][庆祝][礼物][红包][发财][福][烟花][爆竹][猪头][跳跳][发抖][转圈][闪电][刀][足球][瓢虫][發][吼嘿][差劲][爱你][NO][有人@您][有人@你][送心][爱情][飞吻][怄火][磕头][回头][跳绳][投降][冷汗][饥饿][疯了][糗大了][左哼哼][吓][饭][西瓜][篮球][乒乓][心][大笑][比心][枯萎][Fight][Beckon][Respect][Drool][Shrunken"
emoji_tab = re.split('\] ?\[', emoji_tab)
msg_keys=['url', 'thumb', 'attachtype', 'title', 'des', 'type', 'weappiconurl', 'weappinfotype',
          'sourceusername', 'appname', 'totalLen', 'comment', 'sourcedisplayname', 'pagepath', 'chatusr',
          'content', 'displayname', 'fromusr', 'svrid', 'label', 'location', 'maptype', 'poiid', 'poiname',
          'scale', 'alias', 'certflag', 'city', 'headPic', 'nickname', 'province', 'sex', 'sign', 'username',
          'feedesc', 'invalidtime', 'payMemo', 'paysubtype', 'transcationid', 'transferid', 'href', 'imgSrc',
          'fee', 'feetype', 'outtradeno', 'payMsgType', 'scene', 'status', 'timestamp', 'transid', 'attachUrl',
          'amount', 'headTitle', 'recAmount', 'sendId', 'statusMess', 'totalAmount', 'totalNum', 'message',
          'auth_icon', 'auth_job', 'avatar', 'msgsource', 'fromUsername', 'ticket', 'percard', 'nativeurl',
          'paymsgid', 'sendertitle', 'context', 'msgUrl']

assert set(formed_regs_map.values()).issubset(set(yes_no_map.keys()))
assert set(formed_regs.keys()).issubset(set(sp_words))
assert set(yes_no_map.values()) == set([0, 1])
assert set(yes_no_map.keys()) == sub_classifier_set
