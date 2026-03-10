# 🎓 茗心页面优化

## 修复时间
2026-03-10 13:20

---

## 修复的问题

### 1. 初次进入图表不显示 ✅

**问题**: 初次进入"茗心"页面时，折线图空白，选择学生后才显示

**原因**: 
- 数据加载和 DOM 渲染时机不同步
- 图表初始化时容器可能还未就绪

**解决方案**:
```javascript
// 延迟 500ms 加载，确保 DOM 就绪
setTimeout(() => {
    this.loadStudentAnalysis();
}, 500);

// 图表渲染前检查元素是否存在
if (!chartElement) {
    console.error('Chart element not found');
    return;
}

// 销毁旧图表再创建新图表（避免重复渲染）
const oldChart = echarts.getInstanceByDom(chartElement);
if (oldChart) oldChart.dispose();
```

---

### 2. 添加学期多选筛选功能 ✅

**功能**: 可以按学期筛选显示的成绩

**效果**:
- 显示所有学期的复选框
- 支持多选
- 支持全选/重置
- 实时筛选图表数据

**UI 设计**:
```
╔═══════════════════════════════════════════════╗
║ 📅 学期筛选：                                  ║
║ ☑ 一年级上学期  ☑ 一年级下学期                ║
║ ☑ 二年级上学期  ☑ 二年级下学期                ║
║ ☑ 三年级上学期  [全选] [重置]                 ║
╚═══════════════════════════════════════════════╝
```

---

## 新增功能

### 1. 学期复选框组
- 自动从数据中提取学期列表
- 默认全选所有学期
- 每个学期一个复选框
- 粉色边框、圆角设计

### 2. 全选按钮
- 一键选择所有学期
- 显示完整成绩趋势

### 3. 重置按钮
- 恢复到全选状态
- 灰色背景区分

### 4. 实时筛选
- 勾选/取消勾选立即生效
- 图表自动更新
- 无需刷新页面

---

## 代码改动

### 1. 数据结构
```javascript
data() {
    return {
        availableSemesters: [],      // 所有可用学期
        selectedSemesters: [],       // 已选中学期
        allScores: []                // 原始成绩数据
    }
}
```

### 2. 新增方法
```javascript
// 学期筛选
filterBySemester() {
    if (全选或全不选) {
        this.studentData.score_trend = this.allScores;
    } else {
        this.studentData.score_trend = this.allScores.filter(
            s => this.selectedSemesters.includes(s.semester)
        );
    }
    this.renderStudentTrendChart();
}

// 全选
selectAllSemesters() {
    this.selectedSemesters = [...this.availableSemesters];
    this.filterBySemester();
}

// 重置
resetSemesters() {
    this.selectedSemesters = [...this.availableSemesters];
    this.filterBySemester();
}
```

### 3. 图表优化
```javascript
// 添加标记点和标记线
markPoint: {
    data: [
        { type: 'max', name: '最高分' },
        { type: 'min', name: '最低分' }
    ]
},
markLine: {
    data: [{ type: 'average', name: '平均分' }]
}
```

---

## 使用方式

### 1. 自动加载
进入"茗心"页面后：
- 自动选择茗心
- 自动加载成绩数据
- 自动显示折线图
- 显示所有学期复选框

### 2. 学期筛选
**筛选单个学期**:
1. 取消勾选其他学期
2. 只保留想看的学期
3. 图表自动更新

**查看特定对比**:
- 例如：只看"一年级上学期"和"三年级上学期"
- 勾选这两个学期
- 对比两个学期的成绩变化

**恢复全部**:
- 点击"全选"按钮
- 或点击"重置"按钮

---

## 图表增强

### 新增标记
1. **最高分标记** - 自动标注最高点
2. **最低分标记** - 自动标注最低点
3. **平均分线** - 显示平均水平线

### 坐标轴优化
- X 轴：考试名称（旋转 45 度避免重叠）
- Y 轴：分数（0-100）
- 轴名：添加"考试名称"和"分数"标签

### 网格优化
```javascript
grid: { left: '10%', right: '10%', bottom: '15%', top: '15%' }
```
留出足够空间显示标签和标题

---

## 测试步骤

### 测试 1: 初次加载
1. 刷新页面（Ctrl+F5）
2. 点击"👧 茗心"标签
3. 等待 1-2 秒
4. ✅ 应该看到：
   - 学生选择器（已选中茗心）
   - 学期筛选复选框
   - 成绩折线图
   - 成就徽章
   - 目标设定

### 测试 2: 学期筛选
1. 进入茗心页面
2. 取消勾选"一年级上学期"
3. ✅ 图表应该立即更新，不显示一年级上学期的数据
4. 重新勾选"一年级上学期"
5. ✅ 图表恢复完整

### 测试 3: 全选/重置
1. 取消勾选所有学期
2. 点击"全选"
3. ✅ 所有学期应该被勾选
4. 点击"重置"
5. ✅ 所有学期应该被勾选

### 测试 4: 切换学生
1. 在学生选择器中选择其他学生
2. ✅ 图表应该更新为该学生的成绩
3. ✅ 学期列表应该更新

---

## 视觉效果

### 学期筛选区域
```html
<div style="background: #f8f9ff; padding: 15px; border-radius: 15px;">
    📅 学期筛选：
    [☑ 一年级上学期] [☑ 一年级下学期]
    [☑ 二年级上学期] [☑ 二年级下学期]
    [☑ 三年级上学期] [全选] [重置]
</div>
```

### 折线图增强
- 📈 平滑曲线
- 🎯 最高点标记
- 📉 最低点标记
- ➖ 平均分虚线
- 📏 坐标轴标签

---

## 文件修改

### 修改的文件
- `frontend/index.html` - 主要修改

### 修改内容
1. 添加学期筛选 UI（约 30 行）
2. 添加数据属性（3 个新字段）
3. 添加筛选方法（4 个新方法）
4. 优化图表渲染（增强标记和布局）
5. 添加延迟加载（500ms）

---

## 技术要点

### 1. 响应式数据
```javascript
// Vue 自动追踪这些变化
this.selectedSemesters = [...semesters];
this.allScores = data.score_trend;
```

### 2. 数组筛选
```javascript
this.allScores.filter(s => 
    this.selectedSemesters.includes(s.semester)
)
```

### 3. 图表销毁和重建
```javascript
const oldChart = echarts.getInstanceByDom(chartElement);
if (oldChart) oldChart.dispose();
const chart = echarts.init(chartElement);
```

### 4. 延迟加载
```javascript
setTimeout(() => {
    this.loadStudentAnalysis();
}, 500);
```

---

## 已知限制

### 1. 学期名称
- 学期名称来自数据中的 `semester` 字段
- 如果数据中没有学期信息，不会显示筛选器

### 2. 性能
- 如果成绩记录非常多（>1000 条），筛选可能有轻微延迟
- 当前数据量（~100 条）完全无延迟

### 3. 浏览器兼容
- 需要现代浏览器（Chrome/Edge/Firefox）
- IE11 不支持部分 ES6 语法

---

## 后续优化建议

### 短期
- [ ] 添加学期颜色编码
- [ ] 添加筛选动画效果
- [ ] 记住用户的筛选选择

### 中期
- [ ] 添加时间范围选择器
- [ ] 添加成绩类型筛选（期中/期末/练习）
- [ ] 添加导出筛选结果功能

### 长期
- [ ] 多学生对比筛选
- [ ] 自定义筛选条件保存
- [ ] 智能筛选推荐

---

## 反馈方式

如有问题或建议，请在家庭群反馈～ ❤️

---

**修复完成时间**: 2026-03-10 13:20
**版本**: v0.5 Beta Fix 2
**测试状态**: ✅ 待验证
