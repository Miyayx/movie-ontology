#/usr/bin/python2.7
#encoding=utf-8
import codecs
import platform
v= platform.python_version()

if v.startswith('2') :
    from ConfigParser import ConfigParser
elif v.startswith('3') :
    from configparser import ConfigParser

def common_items(a,b):
    """
    Find the common element of the two lists
    Will change the sequence
    """
    return list(set(a) & set(b))

def diff_items(a,b):
    """
    Find the different element between the two lists
    Will change the sequence
    """
    return list(set(a)^ set(b))

def getPropMap():
    globalPropMap = {
            "type":"<http://keg.tsinghua.edu.cn/movie/property/instanceOf>",
            "subclassOf":"<http://keg.tsinghua.edu.cn/movie/property/subclassOf>",
            "dataType":{
                        "<http://keg.tsinghua.edu.cn/movie/object/label/zh>":"Title",
                        "<http://keg.tsinghua.edu.cn/movie/common/alias>":"alias",
                        "<http://keg.tsinghua.edu.cn/movie/common/summary>":"Summary",
                        "<http://keg.tsinghua.edu.cn/movie/common/description/zh>":"FullText",
                        "<http://keg.tsinghua.edu.cn/movie/common/image>":"Images",
                        "<http://keg.tsinghua.edu.cn/movie/object/description/zh>":"FullText",
                        "<http://keg.tsinghua.edu.cn/movie/common/firstimage>":"FirstImage",
                        "<http://keg.tsinghua.edu.cn/movie/common/imdb>":"imdb",
                        "<http://keg.tsinghua.edu.cn/movie/common/topic_equivalent_webpage>":u"来源网站",
                        "<http://keg.tsinghua.edu.cn/movie/initial_release_date>":u"首映日",
                        "<http://keg.tsinghua.edu.cn/movie/film/runtime>":u"时长",
                        "<http://keg.tsinghua.edu.cn/movie/tv/original_air_date>":u"播出时间",
                        "<http://keg.tsinghua.edu.cn/movie/tv/original_episode_running_time>":u"单集片长",
                        "<http://keg.tsinghua.edu.cn/movie/tv/theme_song/zh>":u"主题曲",
                        "<http://keg.tsinghua.edu.cn/movie/tv/number_of_seasons>":u"季数",
                        "<http://keg.tsinghua.edu.cn/movie/tv/series_number>":u"片序",
                        "<http://keg.tsinghua.edu.cn/movie/rated>":u"评级",
                        "<http://keg.tsinghua.edu.cn/movie/tv/number_of_episodes>":u"集数",
                        "<http://keg.tsinghua.edu.cn/movie/tv/season_number>":u"季序",
                        "<http://keg.tsinghua.edu.cn/movie/country>":u"制片地区",
                        "<http://keg.tsinghua.edu.cn/movie/genres>":u"体裁",
                        "<http://keg.tsinghua.edu.cn/movie/language>":u"语言",
                        "<http://keg.tsinghua.edu.cn/movie/award_list>":u"获奖列表",
                        "<http://keg.tsinghua.edu.cn/movie/film/sequel>":u"续集",
                        "<http://keg.tsinghua.edu.cn/movie/people/birthdate>":u"出生日期",
                        "<http://keg.tsinghua.edu.cn/movie/people/birthplace>":u"出生地",
                        "<http://keg.tsinghua.edu.cn/movie/people/nationality>":u"国籍",
                        "<http://keg.tsinghua.edu.cn/movie/people/gender/zh>":u"性别",
                        "<http://keg.tsinghua.edu.cn/movie/people/height>":u"身高",
                        "<http://keg.tsinghua.edu.cn/movie/people/weight>":u"体重",
                        "<http://keg.tsinghua.edu.cn/movie/people/education/zh>":u"教育",
                        "<http://keg.tsinghua.edu.cn/movie/people/profession/zh>":u"职业",
                        "<http://keg.tsinghua.edu.cn/movie/people/parent/zh>":u"父母",
                        "<http://keg.tsinghua.edu.cn/movie/people/spouse/zh>":u"配偶",
                        "<http://keg.tsinghua.edu.cn/movie/people/children/zh>":u"孩子",
                        "<http://keg.tsinghua.edu.cn/movie/people/religion/zh>":u"宗教",
                        "<http://keg.tsinghua.edu.cn/movie/people/award_list>":u"奖项列表",
                        "<http://keg.tsinghua.edu.cn/movie/common/marriage>":u"婚姻",
                        "<http://keg.tsinghua.edu.cn/movie/common/slibings>":u"兄弟姊妹",
                        "<http://keg.tsinghua.edu.cn/movie/organization/date_founded>":u"成立时间",
                        "<http://keg.tsinghua.edu.cn/movie/organization/organization_locations/zh>":u"总部地点",
                        "<http://keg.tsinghua.edu.cn/movie/organization/business_industry/zh>":u"经营范围",
                        "<http://keg.tsinghua.edu.cn/movie/organization/company_founders/zh>":u"创始人",
                        "<http://keg.tsinghua.edu.cn/movie/organization/board_members/zh>":u"主要成员",
                        "<http://keg.tsinghua.edu.cn/movie/organization/parent_organizations/zh>":u"母公司",
                        "<http://keg.tsinghua.edu.cn/movie/organization/business_nature/zh>":u"公司性质",
                        "<http://keg.tsinghua.edu.cn/movie/organization/child_organizations/zh>":u"子公司",
                        "<http://keg.tsinghua.edu.cn/movie/organization/award_list>":u"获奖情况"
                    },
            "objectType":{
                    "<http://keg.tsinghua.edu.cn/movie/film/distributed_by>":u"发行公司",
                    "<http://keg.tsinghua.edu.cn/movie/tv/produced_by_company>":u"出品公司",
                    "<http://keg.tsinghua.edu.cn/movie/actor_list>":u"演员表",
                    "<http://keg.tsinghua.edu.cn/movie/directed_by>":u"导演",
                    "<http://keg.tsinghua.edu.cn/movie/produced_by>":u"制片人",
                    "<http://keg.tsinghua.edu.cn/movie/written_by>":u"编剧",
                    "<http://keg.tsinghua.edu.cn/movie/cinematograph_by>":u"摄影师",
                    "<http://keg.tsinghua.edu.cn/movie/music_by>":u"音乐指导",
                    "<http://keg.tsinghua.edu.cn/movie/dubbing_performances>":u"配音",
                    "<http://keg.tsinghua.edu.cn/movie/presenter>":u"主持人",
                    "<http://keg.tsinghua.edu.cn/movie/work_list>":u"作品列表",
                    "<http://keg.tsinghua.edu.cn/movie/organization/company>":u"经纪公司",
                    "<http://keg.tsinghua.edu.cn/movie/organization/films_distributed>":u"代表作品"
                },
            "actor_node":{
                        "<http://keg.tsinghua.edu.cn/movie/blanknode/actor_number>":"actor_number",
                        "<http://keg.tsinghua.edu.cn/movie/blanknode/actor_name>":"actor_name",
                        "<http://keg.tsinghua.edu.cn/movie/blanknode/actor_id>":"actor_id"
                },
            "common":{ #not infobox
                "type":"<http://keg.tsinghua.edu.cn/movie/property/instanceOf>",
                "subclassOf":"<http://keg.tsinghua.edu.cn/movie/property/subclassOf>",
                "Title":"<http://keg.tsinghua.edu.cn/movie/object/label/zh>",
                "Summary":"<http://keg.tsinghua.edu.cn/movie/common/summary>",
                "FullText":"<http://keg.tsinghua.edu.cn/movie/common/description/zh>",
                "Images":"<http://keg.tsinghua.edu.cn/movie/common/image>",
                "FirstImage":"<http://keg.tsinghua.edu.cn/movie/common/firstimage>"
                }
    }
    return globalPropMap

class ConfigTool():
    @staticmethod
    def parse_config(fn, section):
        cf = ConfigParser()
        cf.read(fn)
        return dict(cf.items(section))

