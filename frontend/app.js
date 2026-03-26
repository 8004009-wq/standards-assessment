// 标准自评估系统 - 前端应用 (localStorage 版本，支持 GitHub Pages)
const { createApp, ref, computed, onMounted, watch } = Vue;

// 检测是否在 GitHub Pages 上运行
const isGitHubPages = window.location.hostname.includes('github.io');
const API_BASE = isGitHubPages ? '' : localStorage.getItem('apiBase') || '';
const USE_LOCAL_STORAGE = !API_BASE || isGitHubPages;

// localStorage 数据存储键
const STORAGE_KEYS = {
    tasks: 'assessment_tasks',
    templates: 'assessment_templates',
    taskItems: 'assessment_task_items',
    taskResults: 'assessment_task_results'
};

// 默认模板数据
const DEFAULT_TEMPLATES = [
    {
        id: 'dsmm',
        name: 'DSMM 数据安全能力成熟度模型',
        standard: 'GB/T 37988-2019',
        description: '数据安全能力成熟度评估',
        dimensions: 4,
        items: 21,
        levels: '1-5 级'
    },
    {
        id: 'djcp',
        name: '等保 2.0 基本要求',
        standard: 'GB/T 22239-2019',
        description: '网络安全等级保护二级评估',
        dimensions: 2,
        items: 22,
        levels: '二级'
    },
    {
        id: 'grxxb',
        name: '个人信息安全规范',
        standard: 'GB/T 35273-2020',
        description: '个人信息保护合规评估',
        dimensions: 5,
        items: 15,
        levels: '基础'
    },
    {
        id: 'djcp_data_level1',
        name: '等保数据安全基本要求（第一级）',
        standard: 'GA/T 2380-2026',
        description: '信息安全技术 网络安全等级保护数据安全基本要求',
        dimensions: 7,
        items: 10,
        levels: '一级'
    },
    {
        id: 'djcp_data',
        name: '等保数据安全基本要求（第三级）',
        standard: 'GA/T 2380-2026',
        description: '信息安全技术 网络安全等级保护数据安全基本要求',
        dimensions: 7,
        items: 45,
        levels: '三级'
    }
];

// localStorage 工具函数
const StorageAPI = {
    get(key) {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    },
    set(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    },
    getAll(key) {
        return this.get(key) || [];
    },
    add(key, item) {
        const items = this.getAll(key);
        items.push(item);
        this.set(key, items);
        return item;
    },
    update(key, id, updates) {
        const items = this.getAll(key);
        const index = items.findIndex(i => i.id === id);
        if (index !== -1) {
            items[index] = { ...items[index], ...updates };
            this.set(key, items);
            return items[index];
        }
        return null;
    },
    delete(key, id) {
        const items = this.getAll(key);
        const filtered = items.filter(i => i.id !== id);
        this.set(key, filtered);
    },
    getById(key, id) {
        const items = this.getAll(key);
        return items.find(i => i.id === id);
    }
};

// 生成唯一 ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// 初始化模板数据
function initTemplates() {
    let templates = StorageAPI.getAll(STORAGE_KEYS.templates);
    if (templates.length === 0) {
        StorageAPI.set(STORAGE_KEYS.templates, DEFAULT_TEMPLATES);
        return DEFAULT_TEMPLATES;
    }
    return templates;
}

const app = createApp({
    setup() {
        // 状态
        const currentView = ref('tasks');
        const sidebarOpen = ref(false);
        const tasks = ref([]);
        const templates = ref([]);
        const currentTask = ref(null);
        const currentTaskItems = ref([]);
        const currentTaskResult = ref(null);
        const creating = ref(false);
        const stats = ref({ total_tasks: 0, completed_tasks: 0, in_progress_tasks: 0 });

        const newTask = ref({
            name: '',
            organization: '',
            template_id: ''
        });

        // 计算属性
        const selectedTemplateDescription = computed(() => {
            const tpl = templates.value.find(t => t.id === newTask.value.template_id);
            return tpl ? tpl.description : '';
        });

        // API/Storage 适配层
        const api = {
            async getTasks() {
                if (USE_LOCAL_STORAGE) {
                    return StorageAPI.getAll(STORAGE_KEYS.tasks);
                }
                const res = await fetch(`${API_BASE}/tasks`);
                return await res.json();
            },
            async getTemplates() {
                if (USE_LOCAL_STORAGE) {
                    return initTemplates();
                }
                const res = await fetch(`${API_BASE}/templates`);
                return await res.json();
            },
            async getStats() {
                if (USE_LOCAL_STORAGE) {
                    const allTasks = StorageAPI.getAll(STORAGE_KEYS.tasks);
                    const completed = allTasks.filter(t => t.status === 'completed').length;
                    const inProgress = allTasks.filter(t => t.status === 'in_progress').length;
                    return {
                        total_tasks: allTasks.length,
                        completed_tasks: completed,
                        in_progress_tasks: inProgress
                    };
                }
                const res = await fetch(`${API_BASE}/stats`);
                return await res.json();
            },
            async createTask(taskData) {
                if (USE_LOCAL_STORAGE) {
                    const newTaskItem = {
                        id: generateId(),
                        ...taskData,
                        status: 'draft',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString()
                    };
                    StorageAPI.add(STORAGE_KEYS.tasks, newTaskItem);
                    // 初始化任务项
                    const template = templates.value.find(t => t.id === taskData.template_id);
                    if (template) {
                        const items = generateDefaultItems(template);
                        StorageAPI.set(STORAGE_KEYS.taskItems + '_' + newTaskItem.id, items);
                    }
                    return newTaskItem;
                }
                const res = await fetch(`${API_BASE}/tasks`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(taskData)
                });
                return await res.json();
            },
            async getTask(taskId) {
                if (USE_LOCAL_STORAGE) {
                    return StorageAPI.getById(STORAGE_KEYS.tasks, taskId);
                }
                const res = await fetch(`${API_BASE}/tasks/${taskId}`);
                return await res.json();
            },
            async getTaskItems(taskId) {
                if (USE_LOCAL_STORAGE) {
                    return StorageAPI.getAll(STORAGE_KEYS.taskItems + '_' + taskId);
                }
                const res = await fetch(`${API_BASE}/tasks/${taskId}/items`);
                return await res.json();
            },
            async updateTaskItem(taskId, itemId, updates) {
                if (USE_LOCAL_STORAGE) {
                    return StorageAPI.update(STORAGE_KEYS.taskItems + '_' + taskId, itemId, updates);
                }
                const res = await fetch(`${API_BASE}/tasks/${taskId}/items/${itemId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updates)
                });
                return await res.json();
            },
            async deleteTask(taskId) {
                if (USE_LOCAL_STORAGE) {
                    StorageAPI.delete(STORAGE_KEYS.tasks, taskId);
                    localStorage.removeItem(STORAGE_KEYS.taskItems + '_' + taskId);
                    localStorage.removeItem(STORAGE_KEYS.taskResults + '_' + taskId);
                    return;
                }
                await fetch(`${API_BASE}/tasks/${taskId}`, { method: 'DELETE' });
            },
            async getTaskResult(taskId) {
                if (USE_LOCAL_STORAGE) {
                    const cached = StorageAPI.get(STORAGE_KEYS.taskResults + '_' + taskId);
                    if (cached) return cached;
                    // 计算结果
                    const items = StorageAPI.getAll(STORAGE_KEYS.taskItems + '_' + taskId);
                    const result = calculateResult(items);
                    StorageAPI.set(STORAGE_KEYS.taskResults + '_' + taskId, result);
                    return result;
                }
                const res = await fetch(`${API_BASE}/tasks/${taskId}/result`);
                return await res.json();
            }
        };

        // 生成默认评估项
        function generateDefaultItems(template) {
            const items = [];
            const dimensionNames = {
                'dsmm': ['数据采集安全', '数据传输安全', '数据存储安全', '数据处理安全'],
                'djcp': ['安全通用要求', '数据安全扩展要求'],
                'grxxb': ['收集', '使用', '保存', '共享', '删除'],
                'djcp_data_level1': ['数据分类分级', '访问控制', '存储安全', '传输安全', '备份恢复', '安全处置', '监测审计'],
                'djcp_data': ['数据分类分级', '访问控制', '存储安全', '传输安全', '备份恢复', '安全处置', '监测审计']
            };
            
            const dimensions = dimensionNames[template.id] || ['维度 1', '维度 2'];
            const itemsPerDimension = Math.ceil(template.items / dimensions.length);
            
            let itemId = 1;
            dimensions.forEach((dim, dimIndex) => {
                for (let i = 0; i < itemsPerDimension && itemId <= template.items; i++, itemId++) {
                    items.push({
                        id: 'item_' + itemId,
                        dimension: dim,
                        dimension_index: dimIndex + 1,
                        content: `${dim} - 评估项 ${itemId}`,
                        rating: null,
                        evidence: '',
                        remarks: ''
                    });
                }
            });
            
            return items;
        }

        // 计算评估结果
        function calculateResult(items) {
            const ratingScores = {
                compliant: 100,
                partial: 50,
                non_compliant: 0,
                not_applicable: null
            };

            const dimensionScores = {};
            const dimensionCounts = {};
            const levelDistribution = {
                compliant: 0,
                partial: 0,
                non_compliant: 0,
                not_applicable: 0
            };

            let totalScore = 0;
            let validCount = 0;

            items.forEach(item => {
                if (item.rating) {
                    levelDistribution[item.rating]++;
                    if (item.rating !== 'not_applicable') {
                        const score = ratingScores[item.rating];
                        totalScore += score;
                        validCount++;

                        if (!dimensionScores[item.dimension]) {
                            dimensionScores[item.dimension] = 0;
                            dimensionCounts[item.dimension] = 0;
                        }
                        dimensionScores[item.dimension] += score;
                        dimensionCounts[item.dimension]++;
                    }
                }
            });

            // 计算维度平均分
            Object.keys(dimensionScores).forEach(dim => {
                if (dimensionCounts[dim] > 0) {
                    dimensionScores[dim] = Math.round(dimensionScores[dim] / dimensionCounts[dim]);
                }
            });

            const overallCompliance = validCount > 0 ? Math.round(totalScore / validCount) : 0;

            return {
                overall_compliance: overallCompliance,
                dimension_scores: dimensionScores,
                level_distribution: levelDistribution,
                total_items: items.length,
                completed_items: validCount
            };
        }

        // 方法
        const fetchTasks = async () => {
            try {
                tasks.value = await api.getTasks();
            } catch (e) {
                console.error('获取任务失败:', e);
                ElementPlus.ElMessage.error('获取任务列表失败');
            }
        };

        const fetchTemplates = async () => {
            try {
                templates.value = await api.getTemplates();
            } catch (e) {
                console.error('获取模板失败:', e);
                templates.value = DEFAULT_TEMPLATES;
            }
        };

        const fetchStats = async () => {
            try {
                stats.value = await api.getStats();
            } catch (e) {
                console.error('获取统计失败:', e);
            }
        };

        const createTask = async () => {
            if (!newTask.value.name || !newTask.value.template_id) {
                ElementPlus.ElMessage.warning('请填写任务名称和评估标准');
                return;
            }
            creating.value = true;
            try {
                await api.createTask(newTask.value);
                ElementPlus.ElMessage.success('评估任务创建成功');
                newTask.value = { name: '', organization: '', template_id: '' };
                currentView.value = 'tasks';
                fetchTasks();
                fetchStats();
            } catch (e) {
                console.error('创建任务失败:', e);
                ElementPlus.ElMessage.error('创建失败，请重试');
            } finally {
                creating.value = false;
            }
        };

        const openTask = async (task) => {
            try {
                currentTask.value = await api.getTask(task.id);
                currentTaskItems.value = await api.getTaskItems(task.id);
                sidebarOpen.value = true;
                
                // 获取结果分析
                fetchTaskResult(task.id);
            } catch (e) {
                console.error('获取任务详情失败:', e);
                ElementPlus.ElMessage.error('获取任务详情失败');
            }
        };

        const fetchTaskResult = async (taskId) => {
            try {
                currentTaskResult.value = await api.getTaskResult(taskId);
                // 等待 DOM 渲染后再初始化图表
                setTimeout(() => {
                    if (document.getElementById('radarChart')) {
                        renderCharts(currentTaskResult.value);
                    }
                }, 100);
            } catch (e) {
                console.error('获取结果失败:', e);
            }
        };

        const saveItemRating = async (item) => {
            try {
                await api.updateTaskItem(currentTask.value.id, item.id, {
                    rating: item.rating,
                    evidence: item.evidence,
                    remarks: item.remarks
                });
                
                // 重新计算结果
                currentTaskItems.value = await api.getTaskItems(currentTask.value.id);
                fetchTaskResult(currentTask.value.id);
                fetchTasks();
                fetchStats();
                
                ElementPlus.ElMessage.success('保存成功');
            } catch (e) {
                console.error('保存失败:', e);
                ElementPlus.ElMessage.error('保存失败');
            }
        };

        const deleteTask = async (taskId) => {
            try {
                await ElementPlus.ElMessageBox.confirm('确定要删除此评估任务吗？', '确认删除', {
                    type: 'warning'
                });
                await api.deleteTask(taskId);
                ElementPlus.ElMessage.success('删除成功');
                fetchTasks();
                fetchStats();
            } catch (e) {
                if (e !== 'cancel') {
                    console.error('删除失败:', e);
                    ElementPlus.ElMessage.error('删除失败');
                }
            }
        };

        const closeSidebar = () => {
            sidebarOpen.value = false;
            currentTask.value = null;
            currentTaskItems.value = [];
        };

        const selectTemplate = (tpl) => {
            newTask.value.template_id = tpl.id;
        };

        const onViewChange = (view) => {
            if (view === 'stats' && currentTask.value) {
                fetchTaskResult(currentTask.value.id);
            }
        };

        const getComplianceType = (rate) => {
            if (rate >= 80) return 'success';
            if (rate >= 60) return 'warning';
            return 'danger';
        };

        const getStatusLabel = (status) => {
            const labels = {
                draft: '草稿',
                in_progress: '进行中',
                completed: '已完成'
            };
            return labels[status] || status;
        };

        const getRatingType = (rating) => {
            const types = {
                compliant: 'success',
                partial: 'warning',
                non_compliant: 'danger',
                not_applicable: 'info'
            };
            return types[rating] || 'info';
        };

        const renderCharts = (data) => {
            // 清除旧图表
            const radarChartEl = document.getElementById('radarChart');
            const pieChartEl = document.getElementById('pieChart');
            
            if (radarChartEl) {
                radarChartEl.innerHTML = '';
                const radarChart = echarts.init(radarChartEl);
                const dimensions = Object.keys(data.dimension_scores);
                const scores = Object.values(data.dimension_scores);
                
                radarChart.setOption({
                    title: { text: '维度得分分析', left: 'center' },
                    radar: {
                        indicator: dimensions.map(d => ({ name: d, max: 100 })),
                        radius: '65%'
                    },
                    series: [{
                        type: 'radar',
                        data: [{
                            value: scores,
                            name: '得分',
                            areaStyle: { color: 'rgba(102, 126, 234, 0.3)' },
                            lineStyle: { color: '#667eea' }
                        }]
                    }]
                });
            }

            if (pieChartEl) {
                pieChartEl.innerHTML = '';
                const pieChart = echarts.init(pieChartEl);
                pieChart.setOption({
                    title: { text: '评估项分布', left: 'center' },
                    series: [{
                        type: 'pie',
                        radius: '50%',
                        data: [
                            { value: data.level_distribution.compliant, name: '符合' },
                            { value: data.level_distribution.partial, name: '部分符合' },
                            { value: data.level_distribution.non_compliant, name: '不符合' },
                            { value: data.level_distribution.not_applicable, name: '不适用' }
                        ],
                        emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
                    }]
                });
            }
        };

        // 生命周期
        onMounted(() => {
            fetchTasks();
            fetchTemplates();
            fetchStats();
        });

        return {
            currentView,
            sidebarOpen,
            tasks,
            templates,
            currentTask,
            currentTaskItems,
            currentTaskResult,
            creating,
            stats,
            newTask,
            selectedTemplateDescription,
            createTask,
            openTask,
            deleteTask,
            closeSidebar,
            selectTemplate,
            onViewChange,
            getComplianceType,
            getStatusLabel,
            getRatingType,
            saveItemRating
        };
    }
});

app.use(ElementPlus, { locale: ElementPlusLocaleZhCn });
app.mount('#app');
