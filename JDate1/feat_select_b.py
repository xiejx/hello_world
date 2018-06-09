import pandas as pd
import numpy as np

# 读取训练数据
uid_train = pd.read_csv('../train/uid_train.txt',sep='\s+',header=None,names=['uid','label'])
voice_train = pd.read_csv('../train/voice_train.txt',sep='\s+',header=None,names=['uid','opp_num','opp_head','opp_len','start_time','end_time','call_type','in_out'],dtype={'start_time':str,'end_time':str})
sms_train = pd.read_csv('../train/sms_train.txt',sep='\s+',header=None,names=['uid','opp_num','opp_head','opp_len','start_time','in_out'],dtype={'start_time':str})
wa_train = pd.read_csv('../train/wa_train.txt',sep='\t',header=None,names=['uid','wa_name','visit_cnt','visit_dura','up_flow','down_flow','wa_type','date'],dtype={'date':str})

# 读取测试数据
voice_test = pd.read_csv('../test_b/voice_test_b.txt',sep='\t',header=None,names=('uid','opp_num','opp_head','opp_len','start_time','end_time','call_type','in_out'),dtype={'start_time':str,'end_time':str})
sms_test = pd.read_csv('../test_b/sms_test_b.txt',sep='\t',header=None,names=('uid','opp_num','opp_head','opp_len','start_time','in_out'),dtype={'start_time':str})
wa_test = pd.read_csv('../test_b/wa_test_b.txt',sep='\t',header=None,names=('uid','wa_name','visit_cnt','visit_dura','up_flow','down_flow','wa_type','date'),dtype={'date':str})

# 测试集的id
uid_test = pd.DataFrame({'uid':pd.unique(wa_test['uid'])})
uid_test.to_csv('../test_b/uid_test_b.txt',index=None)

# 合并训练集和测试集相同表的数据
voice = pd.concat([voice_train,voice_test],axis=0)
sms = pd.concat([sms_train,sms_test],axis=0)
wa = pd.concat([wa_train,wa_test],axis=0)

# 提取通话记录的特征
voice_opp_num = voice.groupby(['uid'])['opp_num'].agg({'unique_count': lambda x: len(pd.unique(x)),'count':'count'}).add_prefix('voice_opp_num_').reset_index()
voice_opp_head=voice.groupby(['uid'])['opp_head'].agg({'unique_count': lambda x: len(pd.unique(x))}).add_prefix('voice_opp_head_').reset_index()
voice_opp_len=voice.groupby(['uid','opp_len'])['uid'].count().unstack().add_prefix('voice_opp_len_').reset_index().fillna(0)
voice_call_type = voice.groupby(['uid','call_type'])['uid'].count().unstack().add_prefix('voice_call_type_').reset_index().fillna(0)
voice_call_type['voice_call_type_not_1'] = voice_call_type['voice_call_type_2'] + voice_call_type['voice_call_type_3'] + voice_call_type['voice_call_type_4'] + voice_call_type['voice_call_type_5']
voice_in_out = voice.groupby(['uid','in_out'])['uid'].count().unstack().add_prefix('voice_in_out_').reset_index().fillna(0)

# 提取用户的总通话时间，主叫的总时间，被叫的总时间，以及各自的平均时间
start = voice['start_time'].str
end = voice['end_time'].str
s_times = start.slice(0,2).astype('int64') * 3600 * 24 + start.slice(2, 4).astype('int64') * 3600 + start.slice(4, 6).astype('int64') * 60 + start.slice(6, 8).astype('int64')
e_times = end.slice(0,2).astype('int64') * 3600 * 24 + end.slice(2, 4).astype('int64') * 3600 + end.slice(4, 6).astype('int64') * 60 + end.slice(6, 8).astype('int64')
diff = e_times - s_times
temp = pd.DataFrame(diff, columns=['voice_time'])
voice_new = pd.merge(voice, temp, how='left', left_index=True, right_index=True)
gp = voice_new[['uid', 'voice_time']].groupby('uid').sum()
in_out_time = voice_new[['uid', 'voice_time', 'in_out']]
temp_a = in_out_time[in_out_time.in_out == 1].groupby(['uid']).sum()
temp_b = in_out_time[in_out_time.in_out == 0].groupby(['uid']).sum()
gp['voice_in_time'] = temp_a.voice_time
gp['voice_out_time'] = temp_b.voice_time
gp = gp.fillna(0)
voice_in_out = pd.merge(voice_in_out, gp, how='left', left_on='uid', right_index=True)
voice_in_out['voice_in_time_mean'] = voice_in_out.voice_in_time / voice_in_out.voice_in_out_1
voice_in_out['voice_out_time_mean'] = voice_in_out.voice_out_time / voice_in_out.voice_in_out_0
voice_in_out['voice_time_mean'] = voice_in_out.voice_time / (voice_in_out.voice_in_out_0 + voice_in_out.voice_in_out_1)

# 提取短信记录特征
sms_time = sms['start_time'].str
sms_time = sms_time.slice(2, 4).astype('int64')
sms['start_time'] = sms_time
sms.start_time = sms.start_time.map(lambda x: (x // 6) + 1)
sms_opp_num = sms.groupby(['uid'])['opp_num'].agg({'unique_count': lambda x: len(pd.unique(x)),'count':'count'}).add_prefix('sms_opp_num_').reset_index()
sms_opp_head=sms.groupby(['uid'])['opp_head'].agg({'unique_count': lambda x: len(pd.unique(x))}).add_prefix('sms_opp_head_').reset_index()
sms_opp_len=sms.groupby(['uid','opp_len'])['uid'].count().unstack().add_prefix('sms_opp_len_').reset_index().fillna(0)
sms_in_out = sms.groupby(['uid','in_out'])['uid'].count().unstack().add_prefix('sms_in_out_').reset_index().fillna(0)
sms_in_out_time = sms.groupby(['uid','start_time'])['uid'].count().unstack().add_prefix('sms_time_').reset_index().fillna(0)

# 提取网站/App特征
wa_name = wa.groupby(['uid'])['wa_name'].agg({'unique_count': lambda x: len(pd.unique(x)),'count':'count'}).add_prefix('wa_name_').reset_index()
visit_cnt = wa.groupby(['uid'])['visit_cnt'].agg(['std','max','min','median','mean','sum']).add_prefix('wa_visit_cnt_').reset_index()
visit_dura = wa.groupby(['uid'])['visit_dura'].agg(['std','max','min','median','mean','sum']).add_prefix('wa_visit_dura_').reset_index()
up_flow = wa.groupby(['uid'])['up_flow'].agg(['std','max','min','median','mean','sum']).add_prefix('wa_up_flow_').reset_index()
down_flow = wa.groupby(['uid'])['down_flow'].agg(['std','max','min','median','mean','sum']).add_prefix('wa_down_flow_').reset_index()

# 合并特征
feature = [voice_opp_num,voice_opp_head,voice_opp_len,voice_call_type,voice_in_out,sms_opp_num,sms_opp_head,sms_opp_len,sms_in_out,sms_in_out_time,wa_name,visit_cnt,visit_dura,up_flow,down_flow]

# 训练集特征
train_feature = uid_train
for feat in feature:
    train_feature=pd.merge(train_feature,feat,how='left',on='uid')

# 测试集特征
test_feature = uid_test
for feat in feature:
    test_feature=pd.merge(test_feature,feat,how='left',on='uid')

train_feature = train_feature.fillna(0)
test_feature = test_feature.fillna(0)
	
# 保存特征
train_feature.to_csv('../feature/trainb_featureV2.csv',index=None)
test_feature.to_csv('../feature/testb_featureV2.csv',index=None)
