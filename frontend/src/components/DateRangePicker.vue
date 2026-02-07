<template>
  <div class="date-range-picker">
    <div class="calendar">
      <label>Start Date</label>
      <input type="date" v-model="startDateString" @change="validateDates" />
    </div>
    <div class="calendar">
      <label>End Date</label>
      <input type="date" v-model="endDateString" @change="validateDates" />
    </div>
    <div v-if="errorMessage" class="error-message">
      <span class="error-icon" aria-label="Error">&#9888;</span>
      {{ errorMessage }}
    </div>
    <button :disabled="!isValid" @click="applyDates">Apply</button>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';

export default defineComponent({
  name: 'DateRangePicker',
  props: {
    initialStartDate: { type: String, required: true },
    initialEndDate: { type: String, required: true }
  },
  emits: ['update:dates'],
  setup(props, { emit }) {
    const startDateString = ref(props.initialStartDate);
    const endDateString = ref(props.initialEndDate);
    const errorMessage = ref('');
    const isValid = computed(() => {
      if (!startDateString.value || !endDateString.value) return false;
      const start = new Date(startDateString.value);
      const end = new Date(endDateString.value);
      return start <= end;
    });

    const validateDates = () => {
      if (!startDateString.value || !endDateString.value) {
        errorMessage.value = '';
        return;
      }
      const start = new Date(startDateString.value);
      const end = new Date(endDateString.value);
      if (start > end) {
        errorMessage.value = 'Start date must be before end date.';
      } else {
        errorMessage.value = '';
      }
    };

    const applyDates = () => {
      if (isValid.value) {
        emit('update:dates', {
          start: new Date(startDateString.value),
          end: new Date(endDateString.value)
        });
      }
    };

    // Emit initial dates on mount
    onMounted(() => {
      if (isValid.value) {
        emit('update:dates', {
          start: new Date(startDateString.value),
          end: new Date(endDateString.value)
        });
      }
    });

    return {
      startDateString,
      endDateString,
      errorMessage,
      isValid,
      validateDates,
      applyDates
    };
  }
});
</script>

<style scoped>
.date-range-picker {
  display: flex;
  gap: 2rem;
  justify-content: center;
  align-items: flex-start;
  flex-wrap: wrap;
}
.calendar {
  display: flex;
  flex-direction: column;
  align-items: center;
}
label {
  margin-bottom: 0.5rem;
}
.error-message {
  color: #d32f2f;
  display: flex;
  align-items: center;
  margin-top: 1rem;
  font-size: 1rem;
}
.error-icon {
  margin-right: 0.5rem;
  font-size: 1.2rem;
}
button {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  font-size: 1rem;
  border-radius: 4px;
  border: none;
  background: #1976d2;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
}
button:disabled {
  background: #bdbdbd;
  cursor: not-allowed;
}
</style>
