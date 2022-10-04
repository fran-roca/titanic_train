

def feature_engineering(train_df, test_df):
    """
        Function to encapsulate the variable engineering task

        Args:
           train_df (DataFrame):  Train dataset.
           test_df (DataFrame):  Test dataset.

        Returns:
           DataFrame, DataFrame. Train and test datasets for the model.
    """
    train_df = create_domain_knowledge_features(train_df)
    test_df = create_domain_knowledge_features(test_df)

    return train_df.copy(), test_df.copy()


def create_domain_knowledge_features(df):
    """
        Function to create the context variables

        Args:
           df (DataFrame):  Dataset.
        Returns:
           DataFrame. Dataset.
    """
    # creación de variable Child de tipo booleana
    df['Sex_child'] = 0
    df.loc[df.Age < 16, 'Sex_child'] = 1
    df.loc[df.Age < 16, 'Sex_male'] = 0
    df.loc[df.Age < 16, 'Sex_female'] = 0
    return df.copy()