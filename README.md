# 资金流因子复现

实现过程的代码已经上传到GitHub：https://github.com/JerryRocks241/CNIR_factor

#### 研报复现共分为3部分：数据处理，因子数据计算，绩效检验

代码文件中，data_process.py进行数据处理，factor.py进行因子数据计算，performance_test.py进行绩效检验

## 数据处理

### 订单数据选取

由于数据集中缺少逐笔数据，因此在划分大小单时均按照研报第三部分进行：
$$
大单=超大单+大单+中单\\
小单=小单
$$

### 缺失值处理

由于原始数据中存在部分600开头的股票，在某些交易日存在数据缺失，考虑用前值进行填充，填充后如仍有数据缺失的，考虑去除。
通过以上方式去除空值后的股票数量由552变为511，大约丢失了8%的数据

## 因子数据计算

### AShareMoneyFlow因子

由于原始数据集中缺少股票流通市值数据，因此研报中用到流通市值数据计算的两个因子：Net_Inflow_PCT 和Net_Inflow_PCT_ ACT 暂时无法计算，如果时间充足，可能考虑从其他平台量化接口获取流通市值数据进行计算

### IMB指标及MOD修正

研报中使用大单资金额构建IMB指标，并通过MOD修正调整了AShareMoneyFlow因子，提高了因子有效性

### CNIR因子

在前述因子MOD修正后，继续改进得到的因子

## 绩效检验

### RankIC&RankICIR

计算得到的RankIC和RankICIR数据如下：

|          | NI     | NI_ACT     | NIR     | NIR_ACT     |
| -------- | ------ | ---------- | ------- | ----------- |
| RankIC   | 0.0923 | 0.1309     | 0.2988  | 0.2667      |
| RankICIR | 0.1505 | 0.1106     | 0.0013  | -0.0660     |
|          | NI_MOD | NI_ACT_MOD | NIR_MOD | NIR_ACT_MOD |
| RankIC   | 0.2525 | 0.2309     | 0.2669  | 0.2656      |
| RankICIR | 0.1064 | 0.0810     | 0.0451  | 0.0354      |
|          | CNIR   |            |         |             |
| RankIC   | 0.2669 |            |         |             |
| RankICIR | 0.0451 |            |         |             |

可以看到，MOD修正提高了因子绩效，但是由于数据集与研报不同，导致最后得到的结果没有想象中那么好

### 多空收益

根据因子值大小排序进行10分组，调仓频率为日度，不考虑交易费用，得到的多空收益净值曲线如下：

#### NI因子

![020976b0-7158-4fab-9a24-9ad5fa585238](/Users/jerry/Library/Containers/at.EternalStorms.Yoink-demo/Data/Documents/YoinkPromisedFiles.noIndex/yoinkFilePromiseCreationFolder210264B6-2B6B-4A21-AE9D-62A11D39F665/add210264B6-2B6B-4A21-AE9D-62A11D39F665/020976b0-7158-4fab-9a24-9ad5fa585238.png)

#### NIR_MOD因子

![18e73eb4-2b8b-4092-aaf1-8dbb706e2a3a](/Users/jerry/Library/Containers/at.EternalStorms.Yoink-demo/Data/Documents/YoinkPromisedFiles.noIndex/yoinkFilePromiseCreationFolderD56CA9AB-3400-4FD8-BB82-9D400A97E015/addD56CA9AB-3400-4FD8-BB82-9D400A97E015/18e73eb4-2b8b-4092-aaf1-8dbb706e2a3a.png)

#### CNIR因子

![0319d87e-d709-4309-800f-2e702eaa42d8](/Users/jerry/Library/Containers/at.EternalStorms.Yoink-demo/Data/Documents/YoinkPromisedFiles.noIndex/yoinkFilePromiseCreationFolderF86764D2-4B54-4D63-B6EF-FE58FD503886/addF86764D2-4B54-4D63-B6EF-FE58FD503886/0319d87e-d709-4309-800f-2e702eaa42d8.png)

