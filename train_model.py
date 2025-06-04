from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments, \
    DataCollatorWithPadding
from datasets import load_dataset
import torch
import logging

# Настройка CUDA для оптимизации
torch.backends.cuda.enable_mem_efficient_sdp(True)


def train_imdb_model():
    try:
        dataset = load_dataset('imdb')
        tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

        # Динамическая токенизация
        def tokenize(batch):
            return tokenizer(batch['text'], truncation=True, max_length=256)

        tokenized_ds = dataset.map(tokenize, batched=True, load_from_cache_file=True)
        tokenized_ds.set_format("torch", columns=["input_ids", "attention_mask", "label"])

        model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

        training_args = TrainingArguments(
            output_dir='./results',
            num_train_epochs=1,
            per_device_train_batch_size=32,  # Максимально возможный размер
            per_device_eval_batch_size=128,
            fp16=True,  # Смешанная точность
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_dir='./logs',
            report_to="none",
            gradient_accumulation_steps=2,  # Если не влезает большой батч
        )

        trainer = Trainer(
            model=model, 
            args=training_args,
            train_dataset=tokenized_ds['train'],
            eval_dataset=tokenized_ds['test'],            data_collator=data_collator,  # Динамическое заполнение батчей
        )

        trainer.train()
        model.save_pretrained('./distilbert-imdb')
        tokenizer.save_pretrained('./distilbert-imdb')
        return True
    except Exception as e:
        logging.exception("Training failed")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_imdb_model()