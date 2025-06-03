<template>
    <div class="learn-container">
        <!-- 知识地图部分 -->
        <div class="knowledge-map">
            <h1 class="map-title">探索知识地图</h1>
            <p class="map-subtitle">通往编程高峰的必经之路</p>
            <!-- 知识点标签云 -->
            <div class="tag-cloud">
                <el-tag 
                    v-for="tag in knowledgeTags" 
                    :key="tag.id"
                    :type="tag.type"
                    class="knowledge-tag"
                >
                    {{ tag.name }}
                </el-tag>
            </div>
        </div>
        <div style="width:1200px; margin: 0 auto;">
        <!-- 课程分类标签 -->
        <div class="category-tabs">
            <el-tabs v-model="activeTab" class="tabs">
                <el-tab-pane label="力扣精选" name="featured"></el-tab-pane>
                <el-tab-pane label="算法与数据结构" name="algorithm"></el-tab-pane>
                <el-tab-pane label="八股文" name="interview"></el-tab-pane>
                <el-tab-pane label="岗位必备" name="job"></el-tab-pane>
                <el-tab-pane label="会员专享" name="vip"></el-tab-pane>
            </el-tabs>
        </div>

        <!-- 分类选择 -->
        <!-- <div class="category-filter">
            <el-select v-model="selectedCategory" placeholder="选择分类" @change="filterCourses">
                <el-option
                    v-for="item in categories"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                </el-option>
            </el-select>
        </div> -->

        <!-- 算法基础部分 -->
        <div class="course-section">
            <h2 class="section-title">算法基础</h2>
            <div class="course-cards">
                <el-card v-for="course in displayedBasicCourses" :key="course.id" class="course-card">
                    <div class="card-content">
                        <div class="card-header">
                            <img :src="course.image" class="card-image">
                            <!-- <div v-if="course.tag" class="card-tag">{{ course.tag }}</div> -->
                        </div>
                        <div class="card-info">
                            <div class="info-top">
                                <h3 class="card-title">{{ course.title }}</h3>
                                <p class="card-desc">{{ course.description }}</p>
                            </div>
                            <div class="info-bottom">
                                <div class="card-meta">
                                    <span>{{ course.chapters }} 章</span>
                                    <span>{{ course.duration }} 节</span>
                                    <span>{{ course.views }}</span>
                                </div>
                                <div class="card-category">{{ course.category }}</div>
                            </div>
                        </div>
                    </div>
                </el-card>
            </div>
            <div v-if="hasMoreBasicCourses" class="load-more" @click="loadMore('basic')">
                加载更多
            </div>
        </div>

        <!-- 算法进阶部分 -->
        <div class="course-section">
            <h2 class="section-title">算法进阶</h2>
            <div class="course-cards">
                <el-card v-for="course in filteredAdvancedCourses" :key="course.id" class="course-card">
                    <div class="card-content">
                        <img :src="course.image" class="card-image">
                        <div class="card-info">
                            <h3 class="card-title">{{ course.title }}</h3>
                            <p class="card-desc">{{ course.description }}</p>
                            <div class="card-meta">
                                <span>{{ course.chapters }} 章</span>
                                <span>{{ course.duration }} 节</span>
                                <span>{{ course.views }}</span>
                            </div>
                            <div v-if="course.price" class="card-price">
                                <span class="price">¥{{ course.price }}</span>
                                <span class="original-price">¥{{ course.originalPrice }}</span>
                            </div>
                            <div v-if="course.tag" class="card-tag">{{ course.tag }}</div>
                        </div>
                    </div>
                </el-card>
            </div>
            <div class="load-more" @click="loadMore('advanced')">加载更多</div>
        </div>
    </div>
    </div>
</template>

<script>
export default {
    name: 'Learn',
    data() {
        return {
            searchText: '',
            notificationCount: 0,
            activeTab: 'featured',
            knowledgeTags: [
                { id: 1, name: '数组和字符串', type: '' },
                { id: 2, name: '排序算法', type: 'success' },
                { id: 3, name: '二叉树', type: 'warning' },
                { id: 4, name: '动态规划', type: 'danger' },
                { id: 5, name: '递归与回溯', type: 'info' },
                // 添加更多标签...
            ],
            selectedCategory: 'all',
            categories: [
                { value: 'all', label: '全部' },
                { value: 'array', label: '数组' },
                { value: 'string', label: '字符串' },
                { value: 'tree', label: '树' },
                { value: 'dp', label: '动态规划' }
            ],
            basicCourses: [
                {
                    id: 1,
                    title: '算法面试小抄',
                    description: '本 LeetBook 由汇集高频算法面试知识点及其代码模版...',
                    image: 'http://localhost:8000/static/课程封面.jpg',
                    chapters: 3,
                    duration: 35,
                    views: '39,014',
                    tag: '会员专享',
                    category: '数组'
                },
                {
                    id: 2,
                    title: '排序算法',
                    description: '全面上手排序算法——排序算法.',
                    image: 'http://localhost:8000/static/课程封面.jpg',
                    chapters: 6,
                    duration: 55,
                    views: '53,106',
                    tag: '会员专享'
                },
                {
                    id: 3,
                    title: '算法面试小抄',
                    description: '本 LeetBook 由汇集高频算法面试知识点及其代码模版...',
                    image: 'http://localhost:8000/static/课程封面.jpg',
                    chapters: 3,
                    duration: 35,
                    views: '39,014',
                    tag: '会员专享',
                    category: '数组'
                },
                {
                    id: 4,
                    title: '算法面试小抄',
                    description: '本 LeetBook 由汇集高频算法面试知识点及其代码模版...',
                    image: 'http://localhost:8000/static/课程封面.jpg',
                    duration: 35,
                    views: '39,014',
                    tag: '会员专享',
                    category: '数组'
                },
                {
                    id: 5,
                    title: '算法面试小抄',
                    description: '本 LeetBook 由汇集高频算法面试知识点及其代码模版...',
                    image: 'http://localhost:8000/static/课程封面.jpg',
                    chapters: 3,
                    duration: 35,
                    views: '39,014',
                    tag: '会员专享',
                    category: '数组'
                },
                {
                    id: 6,
                    title: '算法面试小抄',
                    description: '本 LeetBook 由汇集高频算法面试知识点及其代码模版...',
                    image: 'http://localhost:8000/static/课程封面.jpg',
                    chapters: 3,
                    duration: 35,
                    views: '39,014',
                    tag: '会员专享',
                    category: '数组'
                },
                {
                    id: 7,
                    title: '算法面试小抄',
                    description: '本 LeetBook 由汇集高频算法面试知识点及其代码模版...',
                    image: 'http://localhost:8000/static/课程封面.jpg',
                    chapters: 3,
                    duration: 35,
                    views: '39,014',
                    tag: '会员专享',
                    category: '数组'
                },
            ],
            advancedCourses: [
                {
                    id: 1,
                    title: '七日算法特训',
                    description: '大厂面试常见的算法题型及"内嵌"、七步解题法训练...',
                    image: 'http://localhost:8000/static/课程封面.jpg',
                    chapters: 10,
                    duration: 309,
                    views: '22,572',
                    price: '369',
                    originalPrice: '399',
                    tag: '会员专享'
                },
                // 添加更多进阶课程...
            ],
            pageSize: 6,
            basicCurrentPage: 1,
            advancedCurrentPage: 1
        }
    },
    computed: {
        filteredBasicCourses() {
            if (this.selectedCategory === 'all') {
                return this.basicCourses;
            }
            return this.basicCourses.filter(course => 
                course.category === this.getCategoryLabel(this.selectedCategory)
            );
        },
        displayedBasicCourses() {
            return this.filteredBasicCourses.slice(0, this.basicCurrentPage * this.pageSize);
        },
        hasMoreBasicCourses() {
            return this.displayedBasicCourses.length < this.filteredBasicCourses.length;
        },
        filteredAdvancedCourses() {
            if (this.selectedCategory === 'all') {
                return this.advancedCourses;
            }
            return this.advancedCourses.filter(course => 
                course.category === this.getCategoryLabel(this.selectedCategory)
            );
        },
        displayedAdvancedCourses() {
            return this.filteredAdvancedCourses.slice(0, this.advancedCurrentPage * this.pageSize);
        },
        hasMoreAdvancedCourses() {
            return this.displayedAdvancedCourses.length < this.filteredAdvancedCourses.length;
        }
    },
    methods: {
        getCategoryLabel(value) {
            const category = this.categories.find(c => c.value === value);
            return category ? category.label : '';
        },
        filterCourses() {
            // 可以添加额外的过滤逻辑
        },
        loadMore(section) {
            if (section === 'basic') {
                if (this.hasMoreBasicCourses) {
                    this.basicCurrentPage++;
                }
            } else if (section === 'advanced') {
                if (this.hasMoreAdvancedCourses) {
                    this.advancedCurrentPage++;
                }
            }
        },
        resetPagination() {
            this.basicCurrentPage = 1;
            this.advancedCurrentPage = 1;
        }
    },
    watch: {
        selectedCategory() {
            // 当分类改变时重置分页
            this.resetPagination();
        }
    }
}
</script>

<style scoped>
.learn-container {
    width: 100%;
    /* min-height: 100vh; */
    /* background-color: #f4f5f7; */
}

.nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    height: 50px;
    background-color: #fff;
    border-bottom: 1px solid #e4e7ed;
}

.nav-left {
    display: flex;
    gap: 20px;
}

.nav-item {
    text-decoration: none;
    color: #606266;
    font-size: 14px;
    padding: 0 12px;
}

.nav-item.active {
    color: #409eff;
}

.nav-right {
    display: flex;
    align-items: center;
    gap: 20px;
}

.search-input {
    width: 200px;
}

.knowledge-map {
    padding: 40px 20px;
    text-align: center;
    background-color: #fff;
    /* margin: 20px 0; */
}

.map-title {
    font-size: 28px;
    color: #303133;
    margin-bottom: 10px;
}

.map-subtitle {
    color: #909399;
    margin-bottom: 30px;
}

.tag-cloud {
    font-size: 16px;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
    max-width: 800px;
    margin: 0 auto;
}
.knowledge-tag {
    margin: 5px;
    cursor: pointer;
}

.course-section {
    background: #fff;
    padding: 16px;
    margin: 20px auto;
    max-width: 1200px;
    border-radius: 4px;
}

.section-title {
    font-size: 20px;
    color: #495060;
    margin-bottom: 16px;
    font-weight: 500;
    padding-left: 8px;
}

.course-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    /* padding: 0 8px; */
}

.course-card {
    width: 380px;
    height: 100px;
    border: none;
    transition: all 0.3s;
    padding: 0;
}

.course-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-content {
    display: flex;
    flex-direction: row;
    height: 100%;
}

.card-header {
    position: relative;
    margin: 4px;
    /* width: 120px; */
    flex-shrink: 0;
}

.card-image {
    width: 68px;
    height: 92px;
    object-fit: cover;
    border-radius: 4px;
}

.card-info {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 8px 12px;
    flex-grow: 1;
}

.info-top {
    flex-grow: 1;
}

.card-title {
    font-size: 15px;
    color: #495060;
    margin-bottom: 4px;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.card-desc {
    font-size: 12px;
    color: #666;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.info-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4px;
}

.card-meta {
    display: flex;
    gap: 12px;
    color: #999;
    font-size: 12px;
}

.card-category {
    color: #409EFF;
    font-size: 12px;
}

.card-tag {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(255,107,107,0.9);
    color: #fff;
    padding: 1px 6px;
    border-radius: 2px;
    font-size: 12px;
}

/* .load-more {
    text-align: center;
    color: #666;
    padding: 12px 0;
    cursor: pointer;
    margin-top: 16px;
    background: #f5f5f5;
    border-radius: 4px;
    font-size: 13px;
    transition: background-color 0.3s;
} */
.load-more {
    margin-top: 16px;
    margin-left: auto;
    margin-right: auto;

    background-color: rgba(var(--dsw-lc-button-secondary-rgba));
    border-radius: 8px;
    width: 182px;
    height: 32px;
    line-height: 32px;
    text-align: center;
    font-size: 14px;
    font-weight: 400;
    /* margin: 0 auto; */
    cursor: pointer;
}
.load-more:hover {
    background: #e8e8e8;
}

.category-tabs {
    margin-top: 20px;
    background: #fff;
    padding: 0 20px;
    margin-bottom: 20px;
    margin-left: 0px;
    margin-right: 0px;
    /* margin: 20px auto; */
    max-width: 1200px;
    border-radius: 4px;
}

:deep(.el-tabs__nav-wrap::after) {
    display: none;
}

:deep(.el-tabs__active-bar) {
    display: none;
}

:deep(.el-tabs__item) {
    color: #495060;
    font-size: 16px;
    padding: 0 20px;
}

.category-filter {
    max-width: 1200px;
    margin: 20px auto;
    padding: 0 20px;
}

:deep(.el-card__body) {
    padding: 0;
    height: 100%;
}
</style>