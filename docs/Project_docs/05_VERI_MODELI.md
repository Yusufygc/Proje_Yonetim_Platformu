# Veri Modeli

Bu model SQLite ile başlayacak şekilde tasarlanmıştır. İleride PostgreSQL veya API tabanlı mimariye taşınabilecek isimlendirme ve ilişki yapısı korunmuştur.

## Ana Varlıklar

Önerilen ana tablolar:

- `projects`
- `project_tags`
- `ideas`
- `project_ideas`
- `workflow_stages`
- `project_stages`
- `tasks`
- `checklist_items`
- `decision_records`
- `notes`
- `resources`
- `attachments`
- `activity_logs`
- `settings`

## projects

Projelerin ana kaydı.

Alanlar:

- `id`: integer primary key.
- `title`: text, zorunlu.
- `slug`: text, opsiyonel, benzersiz olabilir.
- `short_description`: text.
- `full_description`: text.
- `problem_statement`: text.
- `target_outcome`: text.
- `project_type`: text.
- `status`: text.
- `priority`: text.
- `health`: text.
- `progress_percent`: integer.
- `github_url`: text.
- `demo_url`: text.
- `docs_url`: text.
- `start_date`: text.
- `target_end_date`: text.
- `completed_at`: text.
- `is_featured`: integer.
- `is_archived`: integer.
- `display_order`: integer.
- `created_at`: text.
- `updated_at`: text.

Not:

- `progress_percent` ilk sürümde manuel veya checklist/görevlerden türetilmiş olabilir. Tek kaynak seçimi açık karardır.

## project_tags

Projeleri sınıflandırmak için.

Alanlar:

- `id`
- `project_id`
- `tag_name`

Kural:

- Aynı proje içinde aynı tag tekrar etmemeli.

## ideas

Projeye dönüşmemiş veya projeye bağlanmış fikirler.

Alanlar:

- `id`
- `title`
- `problem`
- `solution`
- `target_user`
- `expected_value`
- `status`
- `priority`
- `effort`
- `confidence`
- `notes`
- `source`
- `created_at`
- `updated_at`
- `converted_project_id`

## project_ideas

Bir projenin birden fazla fikirden beslenebilmesi için bağlantı tablosu.

Alanlar:

- `id`
- `project_id`
- `idea_id`
- `relation_type`
- `created_at`

Örnek `relation_type` değerleri:

- `SOURCE`
- `RELATED`
- `MERGED`
- `FOLLOW_UP`

## workflow_stages

Varsayılan süreç şablonları.

Alanlar:

- `id`
- `name`
- `description`
- `display_order`
- `is_default`

Örnek kayıtlar:

- Fikir.
- Analiz.
- Tasarım.
- Geliştirme.
- Test.
- Yayın.
- Bakım.
- Tamamlandı.

## project_stages

Her projenin kendi süreç aşamaları.

Alanlar:

- `id`
- `project_id`
- `name`
- `description`
- `status`
- `display_order`
- `started_at`
- `completed_at`
- `acceptance_criteria`

## tasks

Görevlerin ana kaydı.

Alanlar:

- `id`
- `project_id`
- `stage_id`
- `title`
- `description`
- `type`
- `status`
- `priority`
- `due_date`
- `estimated_minutes`
- `spent_minutes`
- `display_order`
- `created_at`
- `updated_at`
- `completed_at`

## checklist_items

Görev içi yapılacak maddeleri.

Alanlar:

- `id`
- `task_id`
- `text`
- `is_done`
- `display_order`
- `created_at`
- `completed_at`

## decision_records

Proje kararları.

Alanlar:

- `id`
- `project_id`
- `stage_id`
- `title`
- `context`
- `decision`
- `alternatives`
- `rationale`
- `impact`
- `status`
- `created_at`
- `updated_at`

## notes

Proje notları.

Alanlar:

- `id`
- `project_id`
- `stage_id`
- `task_id`
- `note_type`
- `title`
- `body`
- `created_at`
- `updated_at`

## resources

Bağlantılar ve referanslar.

Alanlar:

- `id`
- `project_id`
- `idea_id`
- `task_id`
- `title`
- `url`
- `resource_type`
- `description`
- `created_at`
- `updated_at`

## attachments

Yerel dosya, görsel veya çıktı saklama.

Alanlar:

- `id`
- `project_id`
- `task_id`
- `decision_id`
- `file_path`
- `caption`
- `attachment_type`
- `display_order`
- `created_at`

## activity_logs

Otomatik olay geçmişi.

Alanlar:

- `id`
- `project_id`
- `entity_type`
- `entity_id`
- `action`
- `summary`
- `metadata_json`
- `created_at`

Örnek:

```json
{
  "action": "TASK_COMPLETED",
  "summary": "Login ekranı wireframe görevi tamamlandı.",
  "metadata": {
    "task_id": 42,
    "previous_status": "DEVAM_EDIYOR",
    "new_status": "TAMAMLANDI"
  }
}
```

## İlişki Özeti

- Bir proje çok sayıda görev içerir.
- Bir proje çok sayıda süreç aşaması içerir.
- Bir görev opsiyonel olarak bir süreç aşamasına bağlıdır.
- Bir görev çok sayıda checklist maddesi içerir.
- Bir proje çok sayıda karar, not, kaynak ve ek içerir.
- Bir fikir tek projeye dönüştürülebilir ama birden fazla projeyle ilişkili olabilir.
- Aktivite kayıtları proje merkezlidir.

## MVP İçin Minimum Şema

İlk sürümde şu tablolar yeterli olabilir:

- `projects`
- `project_tags`
- `ideas`
- `project_stages`
- `tasks`
- `checklist_items`
- `decision_records`
- `notes`
- `resources`
- `activity_logs`

`attachments` ikinci faza bırakılabilir.

