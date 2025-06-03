<template>
    <div class="announcement-detail">
        <div class="detail-header">
            <h3>{{ title }}</h3>
            <el-button type="text" class="back-btn" @click="$emit('back')">Back</el-button>
        </div>
        <div class="detail-meta">
            {{ formatDate(create_time) }}
            <span class="author">By {{ created_by?.username || 'root' }}</span>
        </div>
        <div class="announcement-content ck-content" v-html="announcement_content"></div>
    </div>
</template>

<script>
import { formatDate } from '@/utils/format.js'
import announcementApi from '@/api/home/announcement.js'

export default {
    name: 'Announcement',
    props: {
        activeAnnouncementId: {
            type: Number,
            required: true
        },
        title: {
            type: String,
            required: true
        },
        create_time: {
            type: String,
            required: true
        },
        created_by: {
            type: Object,
            required: true,
            default: () => ({ username: 'root' })
        }
    },
    data() {
        return {
            announcement_content: null
        }
    },
    methods: {
        formatDate,
        async fetchAnnouncementDetail() {
            try {
                if (!this.activeAnnouncementId) {
                    console.error('No announcement ID provided')
                    return
                }
                const response = await announcementApi.getAnnouncementDetail(this.activeAnnouncementId)
                if (response.code == 0) {
                    console.log(response)
                    let content = response.data.announcement.content
                    // 处理图片路径
                    if (content) {
                        content = content.replace(
                            /src="([^"]+)"/g,
                            (match, url) => {
                                if (url.startsWith('http://') || url.startsWith('https://')) {
                                    return `src="${url}"`
                                }
                                return `src="http://localhost:8000${url}"`
                            }
                        )
                    }
                    this.announcement_content = content
                }
            } catch (error) {
                console.error('Error fetching announcement detail:', error)
            }
        }
    },
    // created() {
    //     this.fetchAnnouncementDetail()
    // },
    watch: {
        activeAnnouncementId: {
            handler(newId) {
                if (newId) {
                    this.fetchAnnouncementDetail()
                }
            },
            immediate: true
        }
    }
}
</script>

<style scoped>

</style>
