<template>
	<homeSlideshow style="margin-top: 20px;"></homeSlideshow>
	<div>
		<div>
			<div v-if="!activeAnnouncementId" class="section-header">
				<div>Competition Announcements</div>
				<el-button type="primary" size="small" @click="refresh">刷新</el-button>
			</div>
			<div v-if="!activeAnnouncementId" class="announcement-list">
				<div v-for="announcement in announcements" :key="announcement.id" class="announcement-item" @click="toggleAnnouncement(announcement.id)">
					<div class="announcement-header">
						<div class="header-left">{{ announcement.title }}</div>
						<div class="header-right">
							<span class="time">{{ formatDate(announcement.create_time) }}</span>
							<span class="author">By {{ announcement.created_by?.username || 'root' }}</span>
						</div>
					</div>
				</div>
			</div>
			<div v-else>
				<Announcement 
					:activeAnnouncementId="activeAnnouncementId"
					:title="currentAnnouncement.title"
					:create_time="currentAnnouncement.create_time"
					:created_by="currentAnnouncement.created_by"
					@back="toggleAnnouncement(null)" 
				/>
			</div>
			<div class="pagination" v-if="!activeAnnouncementId">
				<el-pagination
					background
					layout="prev, pager, next"
					:total="10"
					:current-page="currentPage"
					@current-change="handlePageChange"
				/>
			</div>
		</div>
	</div>
</template>

<script>
import Announcement from '@/components/blog/Announcement.vue'
import announcementsApi from '@/api/competition/announcements.js'
import { formatDate } from '@/utils/format.js'
export default {
  name: 'ContestAnnouncements',
  components: {
	Announcement,
	},
	data() {
		return {
		announcements: [],
		activeAnnouncementId: null,
		currentPage: 1,
		}
	},
	computed: {
		currentAnnouncement() {
			return this.announcements.find(a => a.id === this.activeAnnouncementId) || {}
		}
	},
	methods: {
		formatDate,
		async fetchAnnouncements() {
			try {
				const response = await announcementsApi.GetAnnouncements(this.$route.params.id)
				if (response.data.code === 0) {
					console.log(response.data)
					this.announcements = response.data.data.announcements
				}
			} catch (error) {
				console.error('Error fetching announcements:', error)
			}
		},
		handlePageChange(page) {
			this.currentPage = page
			this.activeAnnouncementId = null
		},
		refresh() {
			this.fetchAnnouncements()
			this.activeAnnouncementId = null
		},
		toggleAnnouncement(id) {
			this.activeAnnouncementId = id
		}
	},
	created() {
		this.fetchAnnouncements()
	}
}


</script>

<style lang="less">
.containers {
	overflow: hidden;
	padding: 40px;
}

.home-container {
	width: 90%;
	margin: 0 auto;
	color: #495060;
}

.announcement-section {
	margin-top: 20px;
	background: #fff;
	border-radius: 8px;
	box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.section-header {
	padding: 25px 30px;
	/* border-bottom: 1px solid #ebeef5; */
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.section-header div {
	margin: 0;
	font-weight: 500;
	line-height: 30px;
	color: #495060;
	font-size: 21px;
}

.announcement-list {
	padding: 0;
}

.announcement-item {
	margin-bottom: 20px;
	border-bottom: 1px solid #ebeef5;
}

.announcement-header {
	cursor: pointer;
	padding-top: 20px;
	padding-bottom: 20px;
	font-size: 16px;
	margin-left: 30px;
	margin-right: 30px;
	color: #495060;
	border-bottom: 1px solid #ebeef5;
	transition: background-color 0.3s;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.header-left {
	flex: 1;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.header-right {
	margin-right: 50px;
	flex-shrink: 0;
	margin-left: 20px;
	font-size: 14px;
	color: #495060;
}

.header-right .time {
	margin-right: 100px;
}

.header-right .author {
	margin-left: 0;
}

.announcement-detail {
	overflow: hidden;
	padding: 30px;
	background: #fff;
}

.detail-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 10px;
}

.detail-header h3 {
	margin: 0;
	font-size: 18px;
	color: #495060;
}

.back-btn {
	color: #495060;
	font-size: 14px;
}

.detail-meta {
	font-size: 12px;
	color: #495060;
	margin-bottom: 20px;
}

.author {
	margin-left: 10px;
}

.announcement-content {
	font-size: 14px;
	line-height: 1.6;
	color: #495060;
}

.announcement-content :deep(p) {
	margin: 1em 0;
}

.announcement-content :deep(ul),
.announcement-content :deep(ol) {
	padding-left: 2em;
	margin: 1em 0;
}

.announcement-content :deep(li) {
	margin: 0.5em 0;
}

.announcement-content :deep(img) {
	max-width: 100%;
	height: auto;
	margin: 10px auto;
	display: block;
	border-radius: 4px;
}

.announcement-content :deep(pre) {
	background-color: #f6f8fa;
	padding: 16px;
	border-radius: 6px;
	overflow: auto;
	margin: 16px 0;
	font-family: Monaco, Consolas, "Courier New", monospace;
	color: #495060;
}

.announcement-content :deep(code) {
	background-color: #f6f8fa;
	padding: 2px 4px;
	border-radius: 3px;
	font-family: Monaco, Consolas, "Courier New", monospace;
	color: #495060;
}

.announcement-content :deep(blockquote) {
	border-left: 4px solid #dfe2e5;
	margin: 16px 0;
	padding-left: 20px;
	color: #495060;
}

.pagination {
	padding: 20px;
	display: flex;
	justify-content: center;
}

:deep(.home-slideshow) {
	width: 90%;
	margin: 0 auto 30px;
}
</style> 