import { ref } from 'vue'

const isGroupingEnabled = ref(localStorage.getItem('cyber_grouping_enabled') === 'true')

const defaultGroups = [
  { id: 'infra', name: 'Инфраструктура', icon: '🖥', color: '#00f3ff', description: 'Гипервизоры и кластеры' },
  { id: 'mon', name: 'Мониторинг', icon: '📈', color: '#00ff66', description: 'Метрики и дашборды' },
  { id: 'sec', name: 'Безопасность', icon: '🛡', color: '#ffaa00', description: 'Ключи и хранилища' },
  { id: 'services', name: 'Сервисы', icon: '⚡', color: '#a855f7', description: 'Внутренние веб-приложения' }
]

const storedGroups = localStorage.getItem('cyber_custom_groups')
const groups = ref(storedGroups ? JSON.parse(storedGroups) : defaultGroups)

export function useGrouping() {
  const saveGroups = () => {
    localStorage.setItem('cyber_custom_groups', JSON.stringify(groups.value))
  }

  const toggleGrouping = (val) => {
    isGroupingEnabled.value = val !== undefined ? val : !isGroupingEnabled.value
    localStorage.setItem('cyber_grouping_enabled', isGroupingEnabled.value ? 'true' : 'false')
  }

  const addGroup = (groupData) => {
    const id = `grp_${Date.now()}`
    groups.value.push({
      id,
      name: groupData.name || 'Новая группа',
      icon: groupData.icon || '📁',
      color: groupData.color || '#00f3ff',
      description: groupData.description || ''
    })
    saveGroups()
  }

  const deleteGroup = (groupId) => {
    groups.value = groups.value.filter(g => g.id !== groupId && g.name !== groupId)
    saveGroups()
  }

  return {
    isGroupingEnabled,
    groups,
    toggleGrouping,
    addGroup,
    deleteGroup,
    saveGroups
  }
}
